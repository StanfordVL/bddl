import matplotlib.pyplot as plt
import numpy as np 
import os 
import pandas as pd
import seaborn as sns 
import tasknet
from tasknet.task_base import TaskNetTask

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
vol_fig = plt.figure(figsize=(30, 8))
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
obj_fig = plt.figure(figsize=(30, 8))
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
