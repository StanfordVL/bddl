import matplotlib.pyplot as plt
import numpy as np 
from tasknet.task_base import TaskNetTask

activities = [
    "packing_lunches_filtered",
    "assembling_gift_baskets_filtered",
    "organizing_school_stuff_filtered",
    "re-shelving_library_books_filtered",
    "serving_hors_d_oeuvres_filtered",
    "putting_away_toys_filtered",
    "putting_away_Christmas_decorations_filtered",
    "putting_dishes_away_after_cleaning_filtered",
    "cleaning_out_drawers_filtered"
]
instances = [0, 1]
activity_instance_pairs = [(activity, inst) for inst in instances for activity in activities]

# +
tasks = [
    TaskNetTask(atus_activity, task_instance) 
    for atus_activity, task_instance in activity_instance_pairs
]
task_names = [
    f"{task.atus_activity.split('_filtered')[0]}_{task.task_instance}"
    for task in tasks 
]
# -

# +
num_goal_conditions = np.array([len(task.parsed_goal_conditions) for task in tasks])
# -

# # Distribution of number of goal conditions 

fig = plt.figure()
plt.hist(num_goal_conditions,
         bins=5)

