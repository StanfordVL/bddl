'''
This code is lightly adapted from https://github.com/pucrs-automated-planning/pddl-parser
'''

import itertools
import re
import sys
import pprint

from tasknet.config import SUPPORTED_PDDL_REQUIREMENTS as supported_requirements
from tasknet.config import get_definition_filename, READABLE_PREDICATE_NAMES


def scan_tokens(filename):
    with open(filename, 'r') as f:
        # Remove single line comments
        str = re.sub(r';.*$', '', f.read(), flags=re.MULTILINE).lower()
    # Tokenize
    stack = []
    tokens = []
    for t in re.findall(r'[()]|[^\s()]+', str):
        if t == '(':
            stack.append(tokens)
            tokens = []
        elif t == ')':
            if stack:
                toks = tokens
                tokens = stack.pop()
                tokens.append(toks)
            else:
                raise Exception('Missing open parenthesis')
        else:
            tokens.append(t)
    if stack:
        raise Exception('Missing close parenthesis')
    if len(tokens) != 1:
        raise Exception('Malformed expression')
    return tokens[0]


def parse_domain(atus_activity, instance):
    domain_filename = get_definition_filename(
        atus_activity, instance, domain=True)
    tokens = scan_tokens(domain_filename)
    if type(tokens) is list and tokens.pop(0) == 'define':
        domain_name = 'unknown'
        requirements = []
        types = []
        actions = []
        predicates = {}
        while tokens:
            group = tokens.pop(0)
            t = group.pop(0)
            if t == 'domain':
                domain_name = group[0]
            elif t == ':requirements':
                for req in group:
                    if not req in supported_requirements:
                        raise Exception('Requirement %s not supported' % req)
                requirements = group
            elif t == ':predicates':
                predicate_name, arguments = parse_predicates(group)
                if predicate_name in predicates:
                    raise Exception(
                        'Predicate %s defined multiple times' % predicate_name)
                predicates[predicate_name] = arguments
            elif t == ':types':
                types = group
            elif t == ':action':
                name = group.pop(0)
                for act in actions:
                    if act.name == name:
                        raise Exception(
                            'Action %s is defined multiple times' % name)
                actions.append(parse_action(group))
            else:
                print('%s is not recognized in domain' % t)
        return domain_name, requirements, types, actions, predicates
    else:
        raise Exception('File %s does not match domain pattern' %
                        domain_filename)


def parse_predicates(group):
    for pred in group:
        predicate_name = pred.pop(0)
        arguments = {}
        untyped_variables = []
        while pred:
            t = pred.pop(0)
            if t == '-':
                if not untyped_variables:
                    raise Exception('Unexpected hyphen in predicates')
                var_type = pred.pop(0)
                while untyped_variables:
                    arguments[untyped_variables.pop(0)] = var_type
            else:
                untyped_variables.append(t)
        while untyped_variables:
            arguments[untyped_variables.pop(0)] = 'object'
        return predicate_name, arguments


def parse_action(group):
    name = group.pop(0)
    if not isinstance(name, str):
        raise Exception('Action without name definition')
    parameters = []
    positive_preconditions = []
    negative_preconditions = []
    add_effects = []
    del_effects = []
    while group:
        t = group.pop(0)
        if t == ':parameters':
            if not isinstance(group, list):
                raise Exception('Error with %s parameters' % name)
            parameters = []
            untyped_parameters = []
            p = group.pop(0)
            while p:
                t = p.pop(0)
                if t == '-':
                    if not untyped_parameters:
                        raise Exception(
                            'Unexpected hyphen in %s parameters' % name)
                    param_type = p.pop(0)
                    while untyped_parameters:
                        parameters.append(
                            [untyped_parameters.pop(0), param_type])
                else:
                    untyped_parameters.append(t)
            while untyped_parameters:
                parameters.append([untyped_parameters.pop(0), 'object'])
        elif t == ':precondition':
            split_predicates(group.pop(0), positive_preconditions,
                             negative_preconditions, name, ' preconditions')
        elif t == ':effect':
            split_predicates(group.pop(0), add_effects,
                             del_effects, name, ' effects')
        else:
            print('%s is not recognized in action' % t)
    return Action(name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects)


def parse_problem(atus_activity, task_instance, domain_name):
    problem_filename = get_definition_filename(atus_activity, task_instance)
    tokens = scan_tokens(problem_filename)
    if isinstance(tokens, list) and tokens.pop(0) == 'define':
        problem_name = 'unknown'
        objects = {}
        initial_state = []
        goal_state = []
        while tokens:
            group = tokens.pop()
            t = group[0]
            if t == 'problem':
                problem_name = group[-1]
            elif t == ':domain':
                if domain_name != group[-1]:
                    raise Exception(
                        'Different domain specified in problem file')
            elif t == ':requirements':
                pass
            elif t == ':objects':
                group.pop(0)
                object_list = []
                while group:
                    if group[0] == '-':
                        group.pop(0)
                        objects[group.pop(0)] = object_list
                        object_list = []
                    else:
                        object_list.append(group.pop(0))
                if object_list:
                    if not 'object' in objects:
                        objects['object'] = []
                    objects['object'] += object_list
            elif t == ':init':
                group.pop(0)
                initial_state = group
            elif t == ':goal':
                package_predicates(group[1], goal_state, '', 'goals')
            else:
                print('%s is not recognized in problem' % t)
        return problem_name, objects, initial_state, goal_state
    else:
        raise Exception('File %s does not match problem pattern' %
                        problem_filename)


def split_predicates(group, pos, neg, name, part):
    if not isinstance(group, list):
        raise Exception('Error with ' + name + part)
    if group[0] == 'and':
        group.pop(0)
    else:
        group = [group]
    for predicate in group:
        if predicate[0] == 'not':
            if len(predicate) != 2:
                raise Exception('Unexpected not in ' + name + part)
            # NOTE removed this because I want the negative goals to have "not"
            neg.append(predicate[-1])
        else:
            pos.append(predicate)


def package_predicates(group, goals, name, part):
    if not isinstance(group, list):
        raise Exception('Error with ' + name + part)
    if group[0] == 'and':
        group.pop(0)
    else:
        group = [group]
    for predicate in group:
        goals.append(predicate)


class Action(object):

    def __init__(self, name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects):
        self.name = name
        self.parameters = parameters
        self.positive_preconditions = positive_preconditions
        self.negative_preconditions = negative_preconditions
        self.add_effects = add_effects
        self.del_effects = del_effects

    def __str__(self):
        return 'action: ' + self.name + \
            '\n  parameters: ' + str(self.parameters) + \
            '\n  positive_preconditions: ' + str(self.positive_preconditions) + \
            '\n  negative_preconditions: ' + str(self.negative_preconditions) + \
            '\n  add_effects: ' + str(self.add_effects) + \
            '\n  del_effects: ' + str(self.del_effects) + '\n'

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def groundify(self, objects):
        if not self.parameters:
            yield self
            return
        type_map = []
        variables = []
        for var, type in self.parameters:
            type_map.append(objects[type])
            variables.append(var)
        for assignment in itertools.product(*type_map):
            positive_preconditions = self.replace(
                self.positive_preconditions, variables, assignment)
            negative_preconditions = self.replace(
                self.negative_preconditions, variables, assignment)
            add_effects = self.replace(self.add_effects, variables, assignment)
            del_effects = self.replace(self.del_effects, variables, assignment)
            yield Action(self.name, assignment, positive_preconditions, negative_preconditions, add_effects, del_effects)

    def replace(self, group, variables, assignment):
        g = []
        for pred in group:
            pred = list(pred)
            iv = 0
            for v in variables:
                while v in pred:
                    pred[pred.index(v)] = assignment[iv]
                iv += 1
            g.append(pred)
        return g


######### AESTHETICS UTILS ##########

def flatten_list(li):
    for elem in li:
        if isinstance(elem, list):
            yield from flatten_list(elem)
        else:
            yield elem


def gen_natural_language_condition(parsed_condition, indent=0):
    indent_string = " " * 4 * indent
    # print(parsed_condition)
    term = parsed_condition

    # for term in parsed_condition:
    if isinstance(term, list):
        if any([isinstance(subterm, list) for subterm in term]):
            if term[0] == "and":
                yield f", and\n".join([list(gen_natural_language_condition(subterm, indent=indent + 1))[0] for subterm in term[1:]])
            elif term[0] == "or":
                yield f", or\n".join([list(gen_natural_language_condition(subterm, indent=indent + 1))[0] for subterm in term[1:]]) + \
                    f",\n{indent_string + '    '}or any combination of these"
            elif term[0] == "not":
                yield indent_string + "the following is NOT true:\n" + list(gen_natural_language_condition(term[1], indent=indent + 1))[0]
            elif term[0] == "imply":
                yield indent_string + f"if\n{list(gen_natural_language_condition(term[1], indent=indent + 1))[0]}\n{indent_string}then\n{list(gen_natural_language_condition(term[2], indent=indent + 1))[0]}\n{indent_string}but if not it doesn't matter"
            elif term[0] == "forall":
                yield indent_string + f"for every {nlterm(term[1][0])},\n{list(gen_natural_language_condition(term[2], indent=indent + 1))[0]}"
            elif term[0] == "exists":
                yield indent_string + f"for at least one {nlterm(term[1][0])},\n{list(gen_natural_language_condition(term[2], indent=indent + 1))[0]}"
            elif term[0] == "forn":
                yield indent_string + f"for exactly {term[1][0]} {nlterm(term[2][0])}(s),\n{list(gen_natural_language_condition(term[3], indent=indent + 1))[0]}"
            elif term[0] == "forpairs":
                yield indent_string + f"for pairs of {nlterm(term[1][0])}s and {nlterm(term[2][0])}s,\n{list(gen_natural_language_condition(term[3], indent=indent + 1))[0]}"
            elif term[0] == "fornpairs":
                yield indent_string + f"for exactly {term[1][0]} pairs of {nlterm(term[2][0])}s and {nlterm(term[3][0])}s,\n{list(gen_natural_language_condition(term[4], indent=indent + 1))[0]}"

        else:
            # print(indent)
            if len(term) == 2:
                # fixed_term1 = term[1].lstrip('?').split('.')[0]
                # if '_' in term[1]:
                #     fixed_term1 += term[1].split('_')[-1]
                article1 = "the " if "_" not in term[1] else ""
                desc = READABLE_PREDICATE_NAMES[term[0]
                                                ] if term[0] in READABLE_PREDICATE_NAMES else term[0]
                yield f"{indent_string}{article1}{nlterm(term[1])} is {desc}"
            else:
                article1 = "the " if "_" not in term[1] else ""
                article2 = "the " if "_" not in term[2] else ""
                desc = READABLE_PREDICATE_NAMES[term[0]
                                                ] if term[0] in READABLE_PREDICATE_NAMES else term[0]
                yield f"{indent_string}{article1}{nlterm(term[1])} is {desc} {article2}{nlterm(term[2])}"

    else:
        raise ValueError('encountered non-list:', term)
        yield ''


def nlterm(term):
    natural_term = term.lstrip('?')
    natural_term = natural_term.split('.')[0]
    if '_' in term:
        # print('it is present')
        natural_term += term.split('_')[-1]
    return natural_term


def gen_natural_language_conditions(parsed_conditions):
    return [''.join(list(gen_natural_language_condition(parsed_condition))) for parsed_condition in parsed_conditions]


def add_pddl_whitespace(pddl_file="task_conditions/parsing_tests/test_app_output.pddl", string=None, save=True):
    if string is not None:
        raw_pddl = string
    else:
        with open(pddl_file, "r") as f:
            raw_pddl = f.read()

    total_characters = len(raw_pddl)

    nest_level = 0
    refined_pddl = ""
    new_block = ""
    char_i = 0
    last_paren_type = None
    while char_i < total_characters:
        if raw_pddl[char_i] == "(":
            new_block = '\n' + '    ' * nest_level + raw_pddl[char_i]
            last_paren_type = "("
            char_i += 1
            while (raw_pddl[char_i] not in [' ', ')']) and char_i < total_characters:
                new_block += raw_pddl[char_i]
                char_i += 1
            refined_pddl += new_block + raw_pddl[char_i]
            if raw_pddl[char_i] == ' ':
                nest_level += 1
        elif raw_pddl[char_i] == ")":
            nest_level -= 1
            if last_paren_type == ")":
                refined_pddl += "\n" + '    ' * nest_level
            refined_pddl += raw_pddl[char_i]
            last_paren_type = ")"
        else:
            refined_pddl += raw_pddl[char_i]
        char_i += 1

    if save:
        with open('task_conditions/parsing_tests/test_app_output_whitespace.pddl', 'w') as f:
            f.write(refined_pddl)

    return refined_pddl


def remove_pddl_whitespace(pddl_file='task_conditions/parsing_tests/test_app_output_whitespace.pddl', string=None, save=True):
    if pddl_file is not None:
        with open(pddl_file, 'r') as f:
            raw_pddl = f.read()
    elif string is not None:
        raw_pddl = string
    else:
        raise ValueError('No PDDL given.')

    pddl = ' '.join([substr.lstrip(' ') for substr in raw_pddl.split('\n')])
    print(pddl)
    pddl = [' ' + substr if substr[0] !=
            ')' else substr for substr in pddl.split(' ') if substr]
    print()
    print(pddl)
    pddl = ''.join(pddl)[1:]

    with open('task_conditions/parsing_tests/test_app_output_nowhitespace.pddl', 'w') as f:
        f.write(pddl)

    return pddl


if __name__ == '__main__':
    if sys.argv[1] == 'add':
        refined_pddl = add_pddl_whitespace()
    if sys.argv[1] == 'remove':
        refined_pddl = remove_pddl_whitespace()
    # if sys.argv[1] == 'test_natural':

    # print(refined_pddl)
    # import sys, pprint
    # atus_activity = sys.argv[1]
    # task_instance = sys.argv[2]
    # print('----------------------------')
    # # pprint.pprint(scan_tokens(atus_activity, instance))
    # print('----------------------------')
    # # pprint.pprint(scan_tokens(atus_activity, instance))
    # print('----------------------------')
    atus_activity = "assembling_gift_baskets_filtered"
    task_instance = 0
    domain_name, requirements, types, actions, predicates = parse_domain(
        atus_activity, task_instance)
    problem_name, objects, initial_state, goal_state = parse_problem(
        atus_activity, task_instance, domain_name)
    # print('----------------------------')
    # print('Problem name:', problem_name)
    # print('Objects:', objects)
    # print('Initial state:', initial_state)
    # print('Goal state:', goal_state)
    # test_condition = '''            (exists
    #             (?table.n.02 - table.n.02)
    #             (forall
    #                 (?basket.n.01 - basket.n.01)
    #                 (ontop ?basket.n.01 ?table.n.02)
    #             )
    #         ) '''
    test_condition = goal_state[0]
    pprint.pprint(goal_state[0])
    if sys.argv[1] == 'test_natural':
        result = (test_condition)
        print('\nRESULT:')
        # pprint.pprint(result)
        print(result)
        # print(len(result))
        with open('tester.txt', 'w') as f:
            f.write(''.join(result))
