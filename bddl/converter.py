import re
import ipdb
from bddl.parsing import parse_problem
from bddl.generator import generate_pddl
from pprint import pprint
import glob
from itertools import permutations, combinations
from collections import Sequence
from itertools import chain, count
from copy import deepcopy
import argparse
import os


def clean_variables_recurse(x, objects_list):
    for i in range(len(x)):
        if isinstance(x[i], list):
            clean_variables_recurse(x[i], objects_list)
        else:
            y = x[i].strip('?')
            if y in objects_list:
                x[i] = y


def clean_variables(goal_state, objects):
    objects_list = []
    for k, v in objects.items():
        objects_list.extend(v)
    clean_variables_recurse(goal_state, objects_list)


def substitute(x, var, obj):
    for i in range(len(x)):
        if isinstance(x[i], list):
            substitute(x[i], var, obj)
        else:
            if x[i] == var:
                x[i] = obj


def convert_forpairs(x, objects, mode='one'):
    assert isinstance(x, list)
    assert x[0] == 'forpairs'
    assert len(x) == 4

    var1 = x[1][0]
    var2 = x[2][0]
    t1 = x[1][-1]
    t2 = x[2][-1]
    os1 = objects[t1]
    os2 = objects[t2]

    expr = x[3]

    if mode == 'all':
        y = ['or']
        for os2_ in permutations(os2, len(os2)):
            yy = ['and']
            for o1, o2 in zip(os1, os2_):
                e = deepcopy(expr)
                substitute(e, var1, o1)
                substitute(e, var2, o2)
                yy.append(e)
            y.append(yy)
    elif mode == 'one':
        y = ['and']
        for o1, o2 in zip(os1, os2):
            e = deepcopy(expr)
            substitute(e, var1, o1)
            substitute(e, var2, o2)
            y.append(e)
    else:
        raise ValueError
    return y


def convert_forn(x, objects, mode='one'):
    assert isinstance(x, list)
    assert x[0] == 'forn'
    assert len(x) == 4
    n_list = x[1]
    assert len(n_list) == 1
    n = int(n_list[0])

    var = x[2][0]
    t = x[2][-1]
    os = objects[t]

    expr = x[3]

    if mode == 'all':   # all possible groundings of the quantifier, complete
        y = ['or']
        for s in combinations(os, n):
            yy = ['and']
            for o in s:
                e = deepcopy(expr)
                substitute(e, var, o)
                yy.append(e)
            y.append(yy)
    elif mode == 'one':     # hack, just the first grounding, incomplete
        y = ['and']
        for o in os[:n]:
            e = deepcopy(expr)
            substitute(e, var, o)
            y.append(e)
    else:
        raise ValueError
    return y


def convert_fornpairs(x, objects, mode='one'):
    assert isinstance(x, list)
    assert len(x) == 5
    assert x[0] == 'fornpairs'
    n_list = x[1]
    assert len(n_list) == 1
    n = int(n_list[0])

    var1 = x[2][0]
    var2 = x[3][0]
    t1 = x[2][-1]
    t2 = x[3][-1]
    os1 = objects[t1]
    os2 = objects[t2]

    expr = x[4]

    if mode == 'all':
        y = ['or']
        for os2_ in permutations(os2, len(os2)):
            yy = ['or']
            for z in combinations(zip(os1, os2_), n):
                yyy = ['and']
                for o1, o2 in z:
                    e = deepcopy(expr)
                    substitute(e, var1, o1)
                    substitute(e, var2, o2)
                    yyy.append(e)
                yy.append(yyy)
            y.append(yy)
    elif mode == 'one':
        y = ['and']
        for o1, o2 in os1[:n], os2[:n]:
            e = deepcopy(expr)
            substitute(e, var1, o1)
            substitute(e, var2, o2)
            y.append(e)
    else:
        raise ValueError
    return y


def convert_goal_state(x, objects):
    for i in range(len(x)):
        if isinstance(x[i][0], list):
            convert_goal_state(x[i], objects)
        else:
            if x[i][0] == 'forpairs':
                convert_goal_state(x[i][-1], objects)
                x[i] = convert_forpairs(x[i], objects)
            elif x[i][0] == 'forn':
                convert_goal_state(x[i][-1], objects)
                x[i] = convert_forn(x[i], objects, 'all')
            elif x[i][0] == 'fornpairs':
                convert_goal_state(x[i][-1], objects)
                x[i] = convert_fornpairs(x[i], objects)


def convert(problem_name, objects, initial_state, goal_state):
    convert_goal_state(goal_state, objects)
    clean_variables(goal_state, objects)
    return problem_name, objects, initial_state, goal_state


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('activity')
    parser.add_argument('instance')
    args = parser.parse_args()
    domain = 'igibson'

    problem_name, objects, initial_state, goal_state = parse_problem(
        args.activity, args.instance, domain)
    problem_name, objects, initial_state, goal_state = convert(problem_name,
                                                               objects,
                                                               initial_state,
                                                               goal_state)
    generate_pddl(domain, args.activity, args.instance, problem_name,
                  objects, initial_state, goal_state,
                  out_dir=os.path.realpath(
                      '/iris/u/kylehsu/code/BDDL/bddl/pddl_activity_definitions'))


if __name__ == '__main__':
    main()
