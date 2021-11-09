import bddl
from bddl.activity import *


behavior_activity = "packing_lunches"
activity_definition = 0
simulator_name = "igibson"
backend = "iGibson"

conds = Conditions(behavior_activity, activity_definition, simulator_name, backend)
scope = get_object_scope(conds)
populated_scope = None      # TODO populate scope in iGibson 
init = get_initial_conditions(conds)
goal = get_goal_conditions(conds, populated_scope)
ground = get_ground_goal_state_options(conds, populated_scope)

print("####### Initial #######")
print(init)
print()
print("####### Goal #######")
print(goal)
print()
print("####### Ground #######")
print(ground)
print()

print("####### Goal evaluation #######")
for __ in range(100):
    print(evaluate_goal_conditions(goal))