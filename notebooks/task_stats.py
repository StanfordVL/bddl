import matplotlib.pyplot as plt
import numpy as np 
import os 
import pandas as pd
import seaborn as sns 
import tasknet
from tasknet.task_base import TaskNetTask
from tasknet.condition_evaluation import Negation

# +
COLORS = sns.color_palette("pastel")
sns.set_context("paper")

tasknet.set_backend("iGibson")

# +
skip = ["domain_igibson.pddl", "sliceable_test", "trivial"]
TASK_CONDITIONS_PATH = "C:/Users/igibs/TaskNet/tasknet/task_conditions"
activities = [activity for activity in os.listdir(TASK_CONDITIONS_PATH) if activity not in skip]
task_instances = [0 for __ in range(len(activities))]

def shorten_name(activity):
    
    # Abbreviate verbs 
    activity = "as".join(activity.split("assembling"))
    activity = "aw".join(activity.split("away"))
    activity = "bot".join(activity.split("bottling"))
    activity = "box".join(activity.split("boxing"))
    activity = "bri".join(activity.split("bringing"))
    activity = "bru".join(activity.split("brushing"))
    activity = "chop".join(activity.split("chopping"))
    activity = "cl".join(activity.split("cleaning"))
    activity = "clr".join(activity.split("clearing"))
    activity = "coll".join(activity.split("collecting"))
    activity = "coll".join(activity.split("collect"))
    activity = "decor".join(activity.split("decorations"))
    activity = "def".join(activity.split("defrosting"))
    activity = "fill".join(activity.split("filling"))
    activity = "ins".join(activity.split("installing"))
    activity = "lay".join(activity.split("laying"))
    activity = "load".join(activity.split("loading"))
    activity = "lock".join(activity.split("locking"))
    activity = "make".join(activity.split("making"))
    activity = "mop".join(activity.split("mopping"))
    activity = "move".join(activity.split("moving"))
    activity = "open".join(activity.split("opening"))
    activity = "org".join(activity.split("organizing"))
    activity = "pack".join(activity.split("packing"))
    activity = "pick".join(activity.split("picking"))
    activity = "pol".join(activity.split("polishing"))
    activity = "prep".join(activity.split("preparing"))
    activity = "pres".join(activity.split("preserving"))
    activity = "put".join(activity.split("putting"))
    activity = "shelv".join(activity.split("re-shelving"))
    activity = "rearr".join(activity.split("rearranging"))
    activity = "serv".join(activity.split("serving"))
    activity = "set".join(activity.split("setting"))
    activity = "sort".join(activity.split("sorting"))
    activity = "stor".join(activity.split("storing"))
    activity = "thaw".join(activity.split("thawing"))
    activity = "thr".join(activity.split("throwing"))
    activity = "unpack".join(activity.split("unpacking"))
    activity = "vac".join(activity.split("vacuuming"))
    activity = "wash".join(activity.split("washing"))
    activity = "wat".join(activity.split("watering"))
    activity = "wax".join(activity.split("waxing")) 
    
    # Remove articles and filler words 
    activity = "_".join(activity.split("_an_"))
    activity = "_".join(activity.split("_a_"))
    activity = "_".join(activity.split("_the_"))
    activity = "".join(activity.split("_inside"))
    
    # Cut off after "or", "for", other
    activity = activity.split("_or")[0]
    activity = activity.split("_for")[0]
    
    return activity     


# -

tasks = [
    TaskNetTask(atus_activity, task_instance) 
    for atus_activity, task_instance in zip(activities, task_instances)
]
task_names = [shorten_name(activity) for activity in activities]

# # Volumes

volumes = [
    sorted([len(option) for option in task.ground_goal_state_options])[0]
    for task in tasks 
]


volumes_data = pd.DataFrame(
    data=zip(task_names, volumes), 
    columns=["activity_name", "volume"]
)
volumes_data

# +
vol_fig = plt.figure(figsize=(15, 4))
vol_ax = sns.barplot(
    data=volumes_data.sort_values(by="volume", ascending=False),
    x="activity_name",
    y="volume"
)
plt.xticks(rotation=90)
for i, bar in enumerate(vol_ax.patches):
    bar.set_color(COLORS[i % 10])

plt.savefig("volumes_by_activities.pdf", bbox_inches="tight")
# -

# # Activity-related objects

object_counts = [
    sum(len(insts) for cat, insts in task.objects.items())
    for task in tasks 
]
object_data = pd.DataFrame(
    data=zip(task_names, object_counts),
    columns=["activity_name", "num_activity_related_objects"]
)
object_data

# +
obj_fig = plt.figure(figsize=(15, 4))
obj_ax = sns.barplot(
    data=object_data.sort_values(by="num_activity_related_objects", ascending=False),
    x="activity_name",
    y="num_activity_related_objects"
)
plt.xticks(rotation=90)
for i, bar in enumerate(obj_ax.patches):
    bar.set_color(COLORS[i % 10])

plt.savefig("numrelevantobjects_by_activities.pdf", bbox_inches="tight")
# -

# # Distinct predicates 

# +
predicate_name_map = {
    "inside": "InsideOf",
    "nextto": "NextTo",
    "ontop": "OnTopOf",
    "stained": "Stained",
    "dusty": "Dusty",
    "onfloor": "OnFloor",
    "soaked": "Soaked",
    "open": "Open",
    "sliced": "Sliced",
    "toggled_on": "ToggledOn",
    "under": "Under",
    "touching": "InContact",
    "cooked": "Cooked", 
    "frozen": "Frozen",
    "burnt": "Burnt"
}

def predicate_to_category(predicate):
    kinematics = set(["inside", "nextto", "ontop", "onfloor", "touching", "open", "under"])
    kinematics = kinematics.union(set([predicate_name_map[pred] for pred in kinematics]))
    temperatures = set(["frozen", "cooked", "burnt"])
    temperatures = temperatures.union(set([predicate_name_map[pred] for pred in temperatures]))
    particles = set(["soaked", "stained", "dusty"])
    particles = particles.union(set([predicate_name_map[pred] for pred in particles]))
    mesh_change = set(["sliced"])
    mesh_change = mesh_change.union(set([predicate_name_map[pred] for pred in mesh_change]))
    other = set(["toggled_on"])
    other = other.union(set([predicate_name_map[pred] for pred in other]))
    
    if predicate in kinematics:
        return 0
    if predicate in temperatures:
        return 1 
    if predicate in particles:
        return 2
    if predicate in mesh_change:
        return 3 
    if predicate in other:
        return 4
    raise ValueError("Predicate not typed")
    


# +
ground_goal_predicate_sets = []
for task in tasks:
    minimal_soln = sorted(task.ground_goal_state_options, key=len)[0]
    ground_goal_predicate_set = set()
    for literal in minimal_soln:
        if isinstance(literal.children[0], Negation):
            ground_goal_predicate_set.add(literal.children[0].children[0].STATE_NAME)
        else:
            ground_goal_predicate_set.add(literal.children[0].STATE_NAME)
    ground_goal_predicate_sets.append(ground_goal_predicate_set)
            
predicate_to_num_activities = {predicate: 0 for predicate in predicate_name_map.keys()}
for ground_goal_pred_set in ground_goal_predicate_sets:
    for predicate in predicate_to_num_activities.keys():
        if predicate in ground_goal_pred_set:
            predicate_to_num_activities[predicate] += 1

# +
predicate_data = pd.DataFrame(
    data=predicate_to_num_activities.items(), 
    columns=["predicate", "num_activities"]
)

categories = []
for row in predicate_data.itertuples():
    categories.append(predicate_to_category(row.predicate))
print(categories)
    
predicate_data
# -

pred_fig = plt.figure(figsize=(15, 4))
pred_ax = sns.barplot(
    data=predicate_data,
    x="predicate",
    y="num_activities"
)
plt.xticks(rotation=90)
for i, bar in enumerate(pred_ax.patches):
    bar.set_color(COLORS[categories[i]])


