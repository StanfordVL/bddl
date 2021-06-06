import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np 
import os 
import pandas as pd
from pathlib import Path 
import seaborn as sns 
import tasknet
from tasknet.task_base import TaskNetTask
from tasknet.condition_evaluation import Negation
import urllib 

# +
# COLORS = sns.color_palette("pastel")
tol_muted_hexes = ["#332288", "#117733", "#44AA99", "#88CCEE", "#DDCC77", "#CC6677", "#AA4499", "#882255"]
tol_light_hexes = ["#77AADD", "#EE8866", "#EEDD88", "#FFAABB", "#99DDFF", "#44BB99", "#BBCC33", "#AAAA00", "#DDDDDD"]
tol_light_hexes_monochrome = ["#77AADD", "#99DDFF", "#BBCC33", "#AAAA00"]
tol_bright_hexes = ["#EE7733", "#0077BB", "#33BBEE", "#EE3377", "#CC3311", "#009988", "#BBBBBB"]
okabe_ito_hexes = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
colors = tol_light_hexes
NUM_COLORS = len(colors)
# COLORS = sns.color_palette(colors)

def set_bar_colors(ax, categories=None, hexes=tol_light_hexes):
    # Categorical coloring 
    if categories is not None: 
        palette = sns.color_palette(hexes)
        for i, bar in enumerate(ax.patches):
            bar.set_color(palette[categories[i]])
    
    # Random distinguishing coloring 
    else:
        palette = sns.color_palette(tol_light_hexes_monochrome)
        next_color = 0
        current_color = 0
        for i, bar in enumerate(ax.patches):
            bar.set_color(palette[current_color])
            while next_color == current_color:
                next_color = np.random.choice([0, 1, 2, 3], p=[.32, .32, .18, .18])
            current_color = next_color

sns.set_context("paper")

tasknet.set_backend("iGibson")

Path("times_new_roman.ttf").write_bytes(urllib.request.urlopen("https://github.com/misuchiru03/font-times-new-roman/blob/master/Times%20New%20Roman.ttf?raw=true").read())
mpl.font_manager.fontManager.addfont('times_new_roman.ttf')
mpl.rc("font", family="Times New Roman")


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
import numpy as np 

vol_fig = plt.figure(figsize=(15, 4))
vol_ax = sns.barplot(
    data=volumes_data.sort_values(by="volume", ascending=False),
    x="activity_name",
    y="volume"
)
plt.xticks(rotation=90)
# next_color = 0
# current_color = 0
# for i, bar in enumerate(vol_ax.patches):
# #     bar.set_color(COLORS[i % NUM_COLORS])
#     while next_color == current_color:
#         next_color = np.random.choice([0, 1, 2, 3], p=[.32, .32, .18, .18])
#     current_color = next_color
#     bar.set_color(COLORS[current_color])
set_bar_colors(vol_ax)

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
set_bar_colors(obj_ax)

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
    "burnt": "Burnt",
    "inroom": "InRoom"
}

def predicate_to_category(predicate):
    kinematics = set(["inside", "nextto", "ontop", "onfloor", "touching", "open", "under", "inroom"])
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
# -

# ## Num activities using each predicate

# +
predicate_data = pd.DataFrame(
    data=predicate_to_num_activities.items(), 
    columns=["predicate", "num_activities"]
)

pred_categories = []
for row in predicate_data.itertuples():
    pred_categories.append(predicate_to_category(row.predicate))
print(pred_categories)
    
predicate_data
# -

pred_fig = plt.figure(figsize=(15, 4))
pred_ax = sns.barplot(
    data=predicate_data,
    x="predicate",
    y="num_activities"
)
plt.xticks(rotation=90)
set_bar_colors(pred_ax, pred_categories)

# ## Percent activities enabled with each predicate 

initial_predicate_sets = []
for task in tasks:
    initial_state = task.parsed_initial_conditions 
    initial_predicate_set = set()
    for literal in initial_state:
        if literal[0] == "not":
            initial_predicate_set.add(literal[1][0])
        else:
            initial_predicate_set.add(literal[0])
    initial_predicate_sets.append(initial_predicate_set)

# +
necessary_predicate_sets = [
    initial.union(ground_goal) 
    for initial, ground_goal in zip(initial_predicate_sets, ground_goal_predicate_sets)
]

necessary_predicate_to_num_activities = {predicate: 0 for predicate in predicate_name_map.keys()}
for necessary_pred_set in necessary_predicate_sets:
    for predicate in necessary_predicate_to_num_activities.keys():
        if predicate in necessary_pred_set:
            necessary_predicate_to_num_activities[predicate] += 1

# +
necessary_predicate_data = pd.DataFrame(
    data=necessary_predicate_to_num_activities.items(), 
    columns=["predicate", "num_activities"]
)

nec_pred_categories = []
for row in predicate_data.itertuples():
    nec_pred_categories.append(predicate_to_category(row.predicate))
    
necessary_predicate_data

# +
predicate_order = [
    "inroom",
    "onfloor",
    "ontop",
    "inside",
    "nextto",
    "under",
    "touching",
    "open",
    "stained",
    "dusty",
    "soaked",
    "toggled_on",
    "sliced",
    "cooked",
    "frozen",
    "burnt"
]

necessary_predicate_sets_copy = necessary_predicate_sets[:]
print(necessary_predicate_sets)
activities_enabled = [0 for __ in range(len(predicate_order))]
for i, pred in enumerate(predicate_order):
    for j, pred_set in enumerate(necessary_predicate_sets_copy): 
        if pred in pred_set:
            necessary_predicate_sets_copy[j].remove(pred)
            if not pred_set:
                activities_enabled[i] += 1
print(activities_enabled)
print(sum(activities_enabled))
            
# -

cumulative_preds_data = pd.DataFrame(
    data=zip(predicate_order, list(np.cumsum(activities_enabled))),
    columns=["predicate", "total_activities_enabled"]
)
cum_pred_categories = []
for row in cumulative_preds_data.itertuples():
    cum_pred_categories.append(predicate_to_category(row.predicate))
print(cum_pred_categories)

# +
cum_pred_fig = plt.figure(figsize=(15, 4))
cum_pred_ax = sns.barplot(
    data=cumulative_preds_data,
    x="predicate",
    y="total_activities_enabled"
)
plt.xticks(rotation=90)
set_bar_colors(cum_pred_ax, cum_pred_categories)

plt.savefig("activities_enabled_by_predicate.pdf", bbox_inches="tight")
# -


