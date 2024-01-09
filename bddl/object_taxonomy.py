import copy
import json
import pkgutil

import networkx as nx
import bddl

DEFAULT_HIERARCHY_FILE = pkgutil.get_data(
    bddl.__package__, "generated_data/output_hierarchy_properties.json")


class ObjectTaxonomy(object):
    def __init__(self, hierarchy_type="default"):
        hierarchy_file = DEFAULT_HIERARCHY_FILE 
        self.taxonomy = self._parse_taxonomy(hierarchy_file)

    @staticmethod
    def _parse_taxonomy(json_str):
        """
        Parse taxonomy from hierarchy JSON file.

        :param json_str: str containing JSON-encoded hierarchy.
        :return: networkx.DiGraph corresponding to object hierarchy tree with synsets as nodes and parent-child
            relationships as directed edges from parent to child.
        """
        json_obj = json.loads(json_str)

        taxonomy = nx.DiGraph()
        nodes = [(json_obj, None)]
        while len(nodes) > 0:
            next_nodes = []
            for node, parent in nodes:
                children_names = set()
                if 'children' in node:
                    for child in node['children']:
                        next_nodes.append((child, node))
                        children_names.add(child['name'])
                taxonomy.add_node(node['name'],
                                  categories=node.get('categories', []),
                                  abilities=node['abilities'])
                for child_name in children_names:
                    taxonomy.add_edge(node['name'], child_name)
            nodes = next_nodes
        return taxonomy

    def _get_synset_by_filter(self, filter_fn):
        """
        Gets a single synset matching the given filter function.

        :param filter_fn: Filter function that takes a single synset as input and returns a boolean (True to keep).
        :return: str corresponding to the matching synset, None if no match found.
        :raises: ValueError if more than one matching synset is found.
        """
        matched = [
            synset for synset in self.taxonomy.nodes if filter_fn(synset)]

        if not matched:
            return None
        elif len(matched) > 1:
            raise ValueError("Multiple synsets matched: %s" %
                             ", ".join(matched))

        return matched[0]
    
    def get_all_synsets(self):
        """
        Return all synsets in topology, in topological order (every synsets appears before its descendants)

        :return: list of str corresponding to synsets
        """
        return list(nx.topological_sort(self.taxonomy))

    def get_synset_from_category(self, category):
        """
        Get synset name corresponding to object category.

        :param category: object category to search for.
        :return: str containing matching synset.
        :raises ValueError if multiple matching synsets are found.
        """
        return self._get_synset_by_filter(lambda synset: category in self.get_categories(synset))

    def get_subtree_categories(self, synset):
        """
        Get the object categories matching the subtree of a given synset (by aggregating categories across all the leaf-level descendants).

        :param synset: synset to search
        :return: list of str corresponding to object categories
        """
        if self.is_leaf(synset):
            synsets = [synset]
        else:
            synsets = self.get_leaf_descendants(synset)
        all_categories = []
        for synset in synsets:
            all_categories += self.get_categories(synset)
        return all_categories

    def is_valid_synset(self, synset):
        """
        Check whether a given synset exists within the object taxonomy.

        :param synset: synset to search.
        :return: bool indicating if the synset exists in the taxonomy.
        """
        return self.taxonomy.has_node(synset)

    def get_descendants(self, synset):
        """
        Get the descendant synsets of a synset.

        :param synset: synset to search.
        :return: list of str corresponding to descendant synsets.
        """
        assert self.is_valid_synset(synset)
        return list(nx.algorithms.dag.descendants(self.taxonomy, synset))

    def get_leaf_descendants(self, synset):
        """
        Get the leaf descendant synsets of a synset, e.g. descendant synsets who are also leaf nodes.

        :param synset: synset to search.
        :return: list of str corresponding to leaf descendant synsets.
        """
        return [node for node in self.get_descendants(synset) if self.taxonomy.out_degree(node) == 0]

    def get_ancestors(self, synset):
        """
        Get the ancestor synsets of a synset.

        :param synset: synset to search.
        :return: list of str corresponding to ancestor synsets.
        """
        assert self.is_valid_synset(synset)
        return list(nx.algorithms.dag.ancestors(self.taxonomy, synset))

    def is_descendant(self, synset, potential_ancestor_synset):
        """
        Check whether a given synset is a descendant of another synset.

        :param synset: The synset being searched for as a descendant.
        :param potential_ancestor_synset: The synset being searched for as a parent.
        :return: bool indicating whether synset is a descendant of potential_ancestor_synset.
        """
        assert self.is_valid_synset(synset)
        assert self.is_valid_synset(potential_ancestor_synset)
        return synset in self.get_descendants(potential_ancestor_synset)

    def is_ancestor(self, synset, potential_descendant_synset):
        """
        Check whether a given synset is an ancestor of another synset.

        :param synset: The synset being searched for as an ancestor.
        :param potential_descendant_synset: The synset being searched for as a descendant.
        :return: bool indicating whether synset is an ancestor of potential_descendant_synset.
        """
        assert self.is_valid_synset(synset)
        assert self.is_valid_synset(potential_descendant_synset)
        return synset in self.get_ancestors(potential_descendant_synset)

    def get_abilities(self, synset):
        """
        Get the abilities of a given synset.

        :param synset: synset to search.
        :return: dict in the form of {ability: {param: value}} containing abilities and ability parameters.
        """
        assert self.is_valid_synset(synset), f"Invalid synset: {synset}"
        return copy.deepcopy(self.taxonomy.nodes[synset]['abilities'])

    def get_categories(self, synset):
        """
        Get the object categories matching a given synset.

        :param synset: synset to search.
        :return: list of str corresponding to object categories matching the synset.
        """
        assert self.is_valid_synset(synset)
        return list(self.taxonomy.nodes[synset]['categories'])

    def get_children(self, synset):
        """
        Get the immediate child synsets of a synset.

        :param synset: synset to search.
        :return: list of str corresponding to child synsets.
        """
        assert self.is_valid_synset(synset)
        return list(self.taxonomy.successors(synset))

    def get_parents(self, synset):
        """
        Get the immediate parent synsets of a synset.

        :param synset: synset to search.
        :return: list of str corresponding to parent synset
        """
        assert self.is_valid_synset(synset)

        return list(self.taxonomy.predecessors(synset))

    def is_leaf(self, synset):
        """
        Check whether a given synset is a leaf synset e.g. it has no descendants.

        :param synset: synset to search.
        :return: bool indicating if the synset is a leaf synset.
        """
        assert self.is_valid_synset(synset), "{} is not a valid synset".format(synset)
        return self.taxonomy.out_degree(synset) == 0

    def has_ability(self, synset, ability):
        """
        Check whether the given synset has the given ability.

        :param synset: synset to check.
        :param ability: Ability name to check.
        :return: bool indicating if the synset has the ability.
        """
        return ability in self.get_abilities(synset)


if __name__ == "__main__":
    object_taxonomy = ObjectTaxonomy()
