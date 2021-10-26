"""Generates a text file that matches PDDL spec."""

from bddl.parsing import parse_problem
from pprint import pprint
import ipdb
import os
import re
import subprocess
import glob


def generate_pddl(domain, atus_activity, task_instance, problem_name, objects, initial_state, goal_state,
                  out_dir='generated_activity_definitions'):
    out_str = ''

    # problem
    out_str += f'(define (problem {problem_name})\n'

    # domain
    out_str += f'\t(:domain {domain})\n'

    out_str += '\n'

    # objects
    out_str += f'\t(:objects\n'
    for object_type, object_names in objects.items():
        line = '\t\t'
        line += ' '.join(object_names)
        line += ' - '
        line += f'{object_type}'
        line += '\n'
        out_str += line
    out_str += '\t)\n'

    out_str += '\n'

    # init
    out_str += f'\t(:init\n'

    def write_init(lst, depth=0):
        prev_depth = None
        line = ''
        indent_closing_bracket = False
        for i, l in enumerate(lst):
            if isinstance(l, list):
                if depth > 0 and (depth + 1) != prev_depth:
                    line += '\n'
                line += write_init(l, depth + 1)
                prev_depth = depth + 1
                if depth >= 1:
                    indent_closing_bracket = True
            else:
                if i == 0:
                    line += (depth + 1) * '\t' + '('
                    line += f'{l}'
                else:
                    line += f' {l}'
        if depth != 0:
            line += indent_closing_bracket * (depth + 1) * '\t' + ')\n'
        return line

    out_str += write_init(initial_state)
    out_str += '\t)\n'

    out_str += '\n'

    # goal
    out_str += f'\t(:goal\n'
    out_str += f'\t\t(and\n'

    def write_goal(lst, depth=0):
        prev_depth = None
        line = ''
        indent_closing_bracket = False
        for i, l in enumerate(lst):
            if isinstance(l, list):
                if depth > 0 and (depth + 1) != prev_depth:
                    line += '\n'
                line += write_goal(l, depth + 1)
                prev_depth = depth + 1
                if depth >= 1:
                    indent_closing_bracket = True
            else:
                if i == 0:
                    line += (depth + 2) * '\t' + '('
                    line += f'{l}'
                else:
                    line += f' {l}'
        if depth != 0:
            line += indent_closing_bracket * (depth + 2) * '\t' + ')\n'
        return line

    out_str += write_goal(goal_state)

    out_str += '\t\t)\n'
    out_str += '\t)\n'

    # end
    out_str += ')'

    # replace tabs with 4 spaces
    out_str = re.sub('\t', '    ', out_str)

    filename = f'{out_dir}/{atus_activity}/problem{task_instance}.pddl'
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'a+') as f:
        f.write(out_str)


def test_generator():
    domain = 'igibson'

    original_filenames = glob.glob('activity_definitions/*/*.bddl')
    p = re.compile('activity_definitions/(.*)/problem(.*)\.bddl')
    for original_filename in original_filenames:
        # print(f'{original_filename}')

        # if 'test' in original_filename:
            # print(f'\tignore tests')
            # continue


        m = p.match(original_filename)

        if m is None:
            print(f'{original_filename} does not match')
            continue

        activity, instance = m.groups()

        problem_name, objects, initial_state, goal_state = parse_problem(activity, instance, domain)
        generate_pddl(domain, activity, instance, problem_name, objects, initial_state, goal_state)

        generated_filename = re.sub('activity_conditions', 'generated_activity_conditions', original_filename)

        subprocess.run(['diff', '-ubw', '-I', ';', generated_filename, original_filename])


if __name__ == '__main__':
    test_generator()