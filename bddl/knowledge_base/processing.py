import csv
from collections import defaultdict, Counter
import logging
import os
import json
import glob
import nltk
from bddl.knowledge_base.orm import IntegrityError
from bddl.object_taxonomy import ObjectTaxonomy
from bddl.activity import Conditions, get_all_activities, get_instance_count
from bddl.config import get_definition_filename
import tqdm
from bddl.knowledge_base.models import *
from bddl.knowledge_base.utils import *

class Command():
    help = "generates all the Django objects using data from ig_pipeline, B1K google sheets, and bddl"


    def handle(self, *args, **options):
        self.preparation()
        self.create_synsets()
        self.create_objects()
        self.create_scenes()
        self.create_tasks()
        self.create_transitions()
        self.post_complete_operation()
    

    # =============================== helper functions ===============================
    def preparation(self):
        """
        put any preparation work (e.g. sanity check) here
        """
        print("Running preparation work...")

        nltk.download('wordnet')

        self.object_taxonomy = ObjectTaxonomy()

        # sanity check room types are up to date
        room_types_from_model = set([room_type for _, room_type in ROOM_TYPE_CHOICES])
        with open(f'{os.path.pardir}/bddl/bddl/generated_data/allowed_room_types.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            room_types_from_csv = set([row[0] for row in reader][1:])
        assert room_types_from_model == room_types_from_csv, "room types are not up to date with allowed_room_types.csv"

        # get object rename mapping
        self.object_rename_mapping = {}
        self.obj_rename_mapping_unique_set = set()
        self.obj_rename_mapping_duplicate_set = set()
        with open(f"{os.path.pardir}/ig_pipeline/metadata/object_renames.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                new_cat = row["New Category"].strip()
                obj_name = row["Object name"].strip()
                # sanity checks
                if obj_name != "":
                    assert len(obj_name.split('-')) == 2, f"{obj_name} should only have one \'-\'"
                    obj_id = obj_name.split('-')[1]
                    if obj_id not in self.obj_rename_mapping_unique_set:
                        self.obj_rename_mapping_unique_set.add(obj_id)
                    else:
                        self.obj_rename_mapping_duplicate_set.add(obj_id)
                    self.object_rename_mapping[obj_name] = f"{new_cat}-{obj_id}"
            assert len(self.obj_rename_mapping_duplicate_set) == 0, f"object rename mapping have duplicates: {self.obj_rename_mapping_duplicate_set}"

        print("Finished prep work...")

    def post_complete_operation(self):
        """
        put any post completion work (e.g. update stuff) here
        """
        print("Running post completion operations...")
        self.generate_synset_state()
        # self.generate_object_images()
        # self.nuke_unused_synsets()


    def create_synsets(self):
        """
        create synsets with annotations from propagated_annots_canonical.json and hierarchy from output_hierarchy.json
        """
        from nltk.corpus import wordnet as wn

        print("Creating synsets...")
        for synset_name in tqdm.tqdm(self.object_taxonomy.get_all_synsets()):
            synset_is_custom = not wn_synset_exists(synset_name)  # TODO: use data from hierarchy. synset_sub_hierarchy["is_custom"] == "1"
            if synset_name != canonicalize(synset_name):
                logging.debug(f"synset {synset_name} is not canonicalized!")
            synset_definition = wn.synset(synset_name).definition() if wn_synset_exists(synset_name) else ""
            synset, created = Synset.get_or_create(name=synset_name, defaults={"definition": synset_definition, "is_custom": synset_is_custom})
            parents = self.object_taxonomy.get_parents(synset_name)
            for parent in parents:
                parent_obj = Synset.get(name=parent)
                synset.parents.add(parent_obj)
            cur_ancestors = self.object_taxonomy.get_ancestors(synset_name)
            for ancestor in sorted(cur_ancestors):
                ancestor_obj = Synset.get(name=ancestor)
                synset.ancestors.add(ancestor_obj)

            # Add any categories
            for category in self.object_taxonomy.get_categories(synset_name):
                assert not any(c.name == category for c in Category.all_objects()), f"Category {category} of {synset_name} already exists!"
                Category.get_or_create(name=category, synset=synset)

            # Add any properties
            if created:
                for property_name, params in self.object_taxonomy.get_abilities(synset_name).items():
                    Property.create(synset=synset, name=property_name, parameters=json.dumps(params))
        

    def create_objects(self):
        """
        Create objects and map to categories (with object inventory)
        """
        print("Creating objects...")
        # first get Deletion Queue
        self.deletion_queue = set()
        with open(f"{os.path.pardir}/ig_pipeline/metadata/deletion_queue.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.deletion_queue.add(row["Object"].strip().split("-")[1])
        # then create objects
        with open(f"{os.path.pardir}/ig_pipeline/artifacts/pipeline/object_inventory_future.json", "r") as f:
            inventory = json.load(f)
            for orig_name, provider in tqdm.tqdm(inventory["providers"].items()):
                object_name = self.object_rename_mapping[orig_name] if orig_name in self.object_rename_mapping else orig_name
                if object_name.split("-")[1] in self.deletion_queue:
                    continue

                # Create the object
                category_name = object_name.split("-")[0]
                category, _ = Category.get_or_create(name=category_name)
                object = Object.create(name=object_name, original_name=orig_name, ready=False, provider=provider, category=category)
                if orig_name in inventory["meta_links"]:
                    for meta_link in inventory["meta_links"][orig_name]:
                        meta_link_obj, _ = MetaLink.get_or_create(name=meta_link)
                        object.meta_links.add(meta_link_obj)

        with open(f"{os.path.pardir}/ig_pipeline/artifacts/pipeline/object_inventory.json", "r") as f:
            objs = []
            for orig_name in tqdm.tqdm(json.load(f)["providers"].keys()):
                object_name = self.object_rename_mapping[orig_name] if orig_name in self.object_rename_mapping else orig_name
                if object_name.split("-")[1] not in self.deletion_queue:
                    category_name = object_name.split("-")[0]
                    category, _ = Category.get_or_create(name=category_name)
                    # safeguard to ensure currently available objects are also in future planned dataset
                    assert Object.exists(name=object_name), f"{object_name} in category {category}, which exists in object_inventory.json, is not in object_inventory_future.json!"
                    object = Object.get(name=object_name)
                    object.ready = True
                    objs.append(object)


    def create_scenes(self):
        """
        create scene objects (which stores the room config)
        scene matching to tasks will be generated later when creating task objects
        """
        print("Creating scenes...")
        with open(rf"{os.path.pardir}/ig_pipeline/artifacts/pipeline/combined_room_object_list_future.json", "r") as f:
            planned_scene_dict = json.load(f)["scenes"]
            for scene_name in tqdm.tqdm(planned_scene_dict):
                scene, _ = Scene.get_or_create(name=scene_name)
                for room_name in planned_scene_dict[scene_name]:
                    # TODO: Implement unique_together constraints
                    try:
                        room = Room.create(
                            name=room_name, 
                            type=room_name.rsplit('_', 1)[0], 
                            ready=False, 
                            scene=scene
                        )
                    except IntegrityError:
                        raise Exception(f"room {room_name} in {scene.name} (not ready) already exists!")
                    for orig_name, count in planned_scene_dict[scene_name][room_name].items():
                        if orig_name.split("-")[1] not in self.deletion_queue:
                            object_name = self.object_rename_mapping[orig_name] if orig_name in self.object_rename_mapping else orig_name
                            object, _ = Object.get_or_create(name=object_name, defaults={
                                "original_name": orig_name,
                                "ready": False,
                                "planned": False,
                                "category": Category.get(name=object_name.split("-")[0]),
                            })
                            RoomObject.create(room=room, object=object, count=count)

        with open(rf"{os.path.pardir}/ig_pipeline/artifacts/pipeline/combined_room_object_list.json", "r") as f:
            current_scene_dict = json.load(f)["scenes"]
            for scene_name in tqdm.tqdm(current_scene_dict):
                scene, _ = Scene.get_or_create(name=scene_name)
                for room_name in current_scene_dict[scene_name]:
                    try:
                        room = Room.create(
                            name=room_name, 
                            type=room_name.rsplit('_', 1)[0], 
                            ready=True, 
                            scene=scene
                        )
                    except IntegrityError:
                        raise Exception(f"room {room_name} in {scene.name} (ready) already exists!")
                    for orig_name, count in current_scene_dict[scene_name][room_name].items():
                        if orig_name.split("-")[1] not in self.deletion_queue:
                            object_name = self.object_rename_mapping[orig_name] if orig_name in self.object_rename_mapping else orig_name
                            object, _ = Object.get_or_create(name=object_name, defaults={
                                "original_name": orig_name,
                                "ready": False,
                                "planned": False,
                                "category": Category.get(name=object_name.split("-")[0])
                            })
                            RoomObject.create(room=room, object=object, count=count)


    def create_tasks(self):
        """
        create tasks and map to synsets
        """
        print("Creating tasks...")
        tasks = glob.glob(rf"{os.path.pardir}/bddl/bddl/activity_definitions/*")
        tasks = [(act, inst) for act in get_all_activities() for inst in range(get_instance_count(act))]
        for act, inst in tqdm.tqdm(tasks):
            # Load task definition
            conds = Conditions(act, inst, "omnigibson")
            synsets = set(synset for synset in conds.parsed_objects if synset != "agent.n.01")
            canonicalized_synsets = set(canonicalize(synset) for synset in synsets)
            with open(get_definition_filename(act, inst), "r") as f:
                raw_task_definition = "".join(f.readlines())

            initial_conds, goal_conds = get_initial_and_goal_conditions(conds)
            combined_conds = initial_conds + goal_conds

            # Create task object
            task_name = f"{act}-{inst}"
            task = Task.create(name=task_name, definition=raw_task_definition)
            for predicate in all_task_predicates(combined_conds):
                pred_obj, _ = Predicate.get_or_create(name=predicate)
                task.uses_predicates.add(pred_obj)

            # add any synset that is not currently in the database
            for synset_name in sorted(canonicalized_synsets):
                is_used_as_non_substance, is_used_as_substance = object_substance_match(combined_conds, synset_name)
                is_used_as_fillable = object_used_as_fillable(combined_conds, synset_name)
                # all annotated synsets have been created before, so any newly created synset is illegal
                synset, _ = Synset.get_or_create(name=synset_name)
                synset.is_used_as_substance = synset.is_used_as_substance or is_used_as_substance
                synset.is_used_as_non_substance = synset.is_used_as_non_substance or is_used_as_non_substance
                synset.is_used_as_fillable = synset.is_used_as_fillable or is_used_as_fillable
                synset_used_predicates = object_used_predicates(combined_conds, synset_name)
                if not synset_used_predicates:
                    logging.debug(f"Synset {synset_name} is not used in any predicate in {task_name}")
                for predicate in synset_used_predicates:
                    pred_obj, _ = Predicate.get_or_create(name=predicate)
                    if pred_obj not in synset.used_in_predicates:
                        synset.used_in_predicates.add(pred_obj)
                task.synsets.add(synset)

                # If the synset ever shows up as future or real, check validity
                used_as_future_or_real = "future" in synset_used_predicates or "real" in synset_used_predicates
                if used_as_future_or_real:
                    # Assert that it's used as future in initial and as real in goal
                    initial_preds = object_used_predicates(initial_conds, synset_name)
                    if "future" not in initial_preds:
                        logging.debug(f"Synset {synset_name} is not used as future in initial in {task_name}")
                    if "real" in initial_preds:
                        logging.debug(f"Synset {synset_name} is used as real in initial in {task_name}")

                    goal_preds = object_used_predicates(goal_conds, synset_name)
                    if "real" not in goal_preds:
                        logging.debug(f"Synset {synset_name} is not used as real in goal in {task_name}")
                    if "future" in goal_preds:
                        logging.debug(f"Synset {synset_name} is used as future in goal in {task_name}")

                    task.future_synsets.add(synset)

            # generate room requirements for task
            room_synset_requirements = defaultdict(Counter)  # room[synset] = count
            for cond in leaf_inroom_conds(conds.parsed_initial_conditions, synsets):
                assert len(cond) == 2, f"{task_name}: {str(cond)} not in correct format"
                rr_type = cond[1]
                rr_synset = cond[0]
                room_synset_requirements[rr_type][rr_synset] += 1

            for rr_type, synset_counter in room_synset_requirements.items():
                room_requirement = RoomRequirement.create(task=task, type=rr_type)
                for rsr_synset, count in synset_counter.items():
                    rsr_synset_obj = Synset.get(name=rsr_synset)
                    RoomSynsetRequirement.create(room_requirement=room_requirement, synset=rsr_synset_obj, count=count)


    def create_transitions(self):
        # Load the transition data
        json_paths = glob.glob(f"{os.path.pardir}/bddl/bddl/generated_data/transition_map/tm_jsons/*.json")
        transitions = []
        for jp in json_paths:
            with open(jp) as f:
                transitions.extend(json.load(f))

        # Create the transition objects
        for transition_data in tqdm.tqdm(transitions):
            transition = TransitionRule.create(name=transition_data["rule_name"])
            for synset_name in transition_data["input_objects"].keys():
                synset = Synset.get(name=synset_name)
                transition.input_synsets.add(synset)
            for synset_name in transition_data["output_objects"].keys():
                synset = Synset.get(name=synset_name)
                transition.output_synsets.add(synset)

    def generate_synset_state(self):
        synsets = []
        substances = {s.name for s in Synset.all_objects() for prop in s.properties if prop.name == "substance"}
        for synset in tqdm.tqdm(Synset.all_objects()):
            if synset.name == "entity.n.01": synset.state = STATE_MATCHED   # root synset is always legal
            elif synset.name in substances:
                synset.state = STATE_SUBSTANCE
            elif synset.parents:
                if len(synset.matching_ready_objects) > 0:
                    synset.state = STATE_MATCHED
                elif len(synset.matching_objects) > 0:
                    synset.state = STATE_PLANNED
                else:
                    synset.state = STATE_UNMATCHED
            else:
                synset.state = STATE_ILLEGAL
            synsets.append(synset)


    def nuke_unused_synsets(self):
        # Make repeated passes until we propagate far enough up
        while True:
            removal_names = set()
            for synset in Synset.all_objects():
                # In a given pass, only leaf nodes can be removed
                if synset.children:
                    continue

                # If a synset has objects or task relevance, we can't remove it
                if len(synset.matching_objects) != 0:
                    continue
                
                if synset.n_task_required != 0:
                    continue

                if synset.used_by_transition_rules:
                    continue

                if synset.produced_by_transition_rules:
                    continue

                # Otherwise queue it for removal
                removal_names.add(synset.name)

            if removal_names:
                for s in list(Synset.all_objects()):
                    if s.name in removal_names:
                        s.delete()
            else:
                break



if __name__ == "__main__":
    import IPython
    Command().handle()
    IPython.embed()