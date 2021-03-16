# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import h5py
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd 
import seaborn as sns
import pprint

sns.set_context("paper")

demos_filepath = os.path.join("d:", "examples_pre_hand")
raw_data = []
for demo_file in os.listdir(demos_filepath):
    if "mp4" in demo_file: 
        continue
    raw_data.append(h5py.File(os.path.join(demos_filepath, demo_file), "r"))
    
def convert_name(name):
    if name == "assembling_gift_baskets_filtered":
        return "gift_baskets"
    elif name == "organizing_school_stuff_filtered":
        return "school_stuff"
    elif name == "packing_lunches_filtered":
        return "lunches"
    elif name == "putting_away_toys_filtered":
        return "toys"
    elif name == "serving_hors_d_oeuvres_filtered":
        return "serving"
    elif name == "cleaning_out_drawers_filtered":
        return "drawers"
    elif name == "putting_away_dishes_after_cleaning_filtered":
        return "dishes"
    elif name == "putting_away_Christmas_decorations_filtered":
        return "decorations"
    elif name == "re-shelving_library_books_filtered":
        return "books"
    else:
        return name


# -


# # Distance

# +
records = []
columns = [
    "task_name",
    "task_instance",
    "scene_id",
    "left_total_dist",
    "right_total_dist",
    "body_total_dist"
]

clip = .2

for demo in raw_data: 
    record = []
    record.append(convert_name(demo.attrs["/metadata/task_name"]))
    record.append(demo.attrs["/metadata/task_instance"])
    record.append(demo.attrs["/metadata/scene_id"][:-4])
    
    # total distance 
    left_position = demo["vr"]["vr_device_data"]["left_controller"][:, 1:4]
    right_position = demo["vr"]["vr_device_data"]["right_controller"][:, 1:4]
    body_position = demo["vr"]["vr_device_data"]["vr_position_data"][:, 0:3]
    
    left_delta_position = np.linalg.norm(left_position[1:-1] - left_position[0:-2], axis=1)
    right_delta_position = np.linalg.norm(right_position[1:-1] - right_position[0:-2], axis=1)
    body_delta_position = np.linalg.norm(body_position[1:-1] - body_position[0:-2], axis=1)

    left_delta_position = np.clip(left_delta_position, -clip, clip)
    right_delta_position = np.clip(right_delta_position, -clip, clip)
    body_delta_position = np.clip(body_delta_position, -clip, clip)
    
    record.append(np.sum(left_delta_position))
    record.append(np.sum(right_delta_position))
    record.append(np.sum(body_delta_position))
    
    records.append(record)
    

dist_plotting_data = pd.DataFrame.from_records(records, columns=columns)
# -

# ### Total distance traveled by task - randomly selected scene

# +
# randomly select scenes for some (task, task_id)
choice_fn = lambda obj: obj.loc[np.random.choice(obj.index), :]
dist_data_randomscenes = dist_plotting_data.groupby(["task_name", "task_instance"], as_index=False).apply(choice_fn)

hued_dfs = [
    dist_data_randomscenes[["task_name", "task_instance", "left_total_dist"]].rename(columns={"left_total_dist": "total_dist"}),
    dist_data_randomscenes[["task_name", "task_instance", "right_total_dist"]].rename(columns={"right_total_dist": "total_dist"}),
    dist_data_randomscenes[["task_name", "task_instance", "body_total_dist"]].rename(columns={"body_total_dist": "total_dist"})
]
hued_dfs[0]["device"] = "left"
hued_dfs[1]["device"] = "right"
hued_dfs[2]["device"] = "body"

hued_dist_data_randomscenes = pd.concat(hued_dfs)
hued_dist_data_randomscenes["task_label"] = hued_dist_data_randomscenes["task_name"] + "_" + hued_dist_data_randomscenes["task_instance"].astype(str)
# -

fig = plt.figure()
ax = sns.barplot(
    x="task_label",
    y="total_dist",
    hue="device",
    data=hued_dist_data_randomscenes
)
plt.xticks(rotation=90)
plt.savefig('total_distance_randomscenes.pdf')

# ### Total distance traveled by task - average across scenes

# +
# average distances across different scenes 
dist_data_avg = dist_plotting_data.groupby(['task_name', 'task_instance'], as_index=False).agg(np.mean)

hued_dfs = [
    dist_data_avg[["task_name", "task_instance", "left_total_dist"]].rename(columns={"left_total_dist": "total_dist"}),
    dist_data_avg[["task_name", "task_instance", "right_total_dist"]].rename(columns={"right_total_dist": "total_dist"}),
    dist_data_avg[["task_name", "task_instance", "body_total_dist"]].rename(columns={"body_total_dist": "total_dist"})
]
hued_dfs[0]["device"] = "left"
hued_dfs[1]["device"] = "right"
hued_dfs[2]["device"] = "body"

hued_dist_data_avg = pd.concat(hued_dfs)
hued_dist_data_avg["task_label"] = hued_dist_data_avg["task_name"] + '_' + hued_dist_data_avg["task_instance"].astype(str)
# -

fig = plt.figure()
ax = sns.barplot(
    x="task_label",
    y="total_dist",
    hue="device",
    data=hued_dist_data_avg
)
plt.xticks(rotation=90)
plt.savefig('total_distance_avgacrossscenes.pdf')

# ### Total distance traveled by task - whisker plot across scenes 

# +
hued_dfs = [
    dist_plotting_data[["task_name", "task_instance", "left_total_dist"]].rename(columns={"left_total_dist": "total_dist"}),
    dist_plotting_data[["task_name", "task_instance", "right_total_dist"]].rename(columns={"right_total_dist": "total_dist"}),
    dist_plotting_data[["task_name", "task_instance", "body_total_dist"]].rename(columns={"body_total_dist": "total_dist"})
]
hued_dfs[0]["device"] = "left"
hued_dfs[1]["device"] = "right"
hued_dfs[2]["device"] = "body"

hued_plotting_data = pd.concat(hued_dfs)
hued_plotting_data["task_label"] = hued_plotting_data["task_name"] + '_' + hued_plotting_data["task_instance"].astype(str)
# -

fig = plt.figure()
# ax = sns.stripplot(x="task_label", y="total_dist", data=hued_plotting_data, jitter=0.05)
ax = sns.violinplot(x="task_label", y="total_dist", hue="device", data=hued_plotting_data)
plt.xticks(rotation=90)
plt.savefig("total_distance_range.pdf")


# # Work

# +
records = []
columns = [
    "task_name",
    "task_instance",
    "scene_id",
]

for demo in raw_data: 
    record = []
    record.append(convert_name(demo.attrs["/metadata/task_name"]))
    record.append(demo.attrs["/metadata/task_instance"])
    record.append(demo.attrs["/metadata/scene_id"][:-4])
    
    # distance 
    left_position = demo["vr"]["vr_device_data"]["left_controller"][:, 1:4]
    right_position = demo["vr"]["vr_device_data"]["right_controller"][:, 1:4]
    body_position = demo["vr"]["vr_device_data"]["vr_position_data"][:, 0:3]
    
    left_delta_position = np.linalg.norm(left_position[1:-1] - left_position[0:-2], axis=1)
    right_delta_position = np.linalg.norm(right_position[1:-1] - right_position[0:-2], axis=1)
    body_delta_position = np.linalg.norm(body_position[1:-1] - body_position[0:-2], axis=1)

    left_delta_position = np.clip(-0.2, 0.2, left_delta_position)
    right_delta_position = np.clip(-0.2, 0.2, right_delta_position)
    body_delta_position = np.clip(-0.2, 0.2, body_delta_position)
    
    # force
    left_force = demo['vr']['vr_device_data']['left_controller'][1:, 17:23]
    right_force = demo['vr']['vr_device_data']['right_controller'][1:, 17:23]
    body_force = demo['vr']['vr_device_data']['vr_position_data'][1:, 6:12]
    
    # total work 
    
    
    records.append(record)
    

dist_plotting_data = pd.DataFrame.from_records(records, columns=columns)
# -

# # Time to success 

# +
import tasknet
from tasknet.task_base import TaskNetTask 
tasknet.set_backend("iGibson")

records = []
columns = [
    "task_name",
    "task_instance",
    "scene_id",
    "success",
    "frames_to_success",
    "num_goal_conditions",
    "frames_to_success_normalized_goal",
    "num_ground_goal_conditions",
    "frames_to_success_normalized_ground",
    "total_grasps"
]

for demo in raw_data: 
    record = []
    task_name = (demo.attrs["/metadata/task_name"])
    task_instance = demo.attrs["/metadata/task_instance"]
    record.append(convert_name(task_name))
    record.append(task_instance)
    record.append(demo.attrs["/metadata/scene_id"][:-4])
    
    # frames to reach success 
    satisfied = demo["goal_status"]["satisfied"][:]
    total_frames, total_goal_conds = satisfied.shape
    satisfied_goal_conds_by_frame = np.sum(satisfied, axis=1)
    success_trace = np.nonzero((satisfied_goal_conds_by_frame == float(total_goal_conds)).astype(np.int32))[0]
    success = bool(len(success_trace))
    
    record.append(int(success))
    frames_to_success = success_trace[0] if success else -1
    record.append(frames_to_success)
    
    record.append(total_goal_conds)
    frames_to_success_normalized_goal = frames_to_success / float(total_goal_conds) if success else -1
    record.append(frames_to_success_normalized_goal)
    
    # normalized frames to reach success 
    task = TaskNetTask(task_name, int(task_instance))
    task.gen_goal_conditions()
    task.gen_ground_goal_conditions()
    avg_ground_goal_conditions = np.mean(np.array([len(option) for option in task.ground_goal_state_options]))    
    record.append(avg_ground_goal_conditions)
    frames_to_success_normalized_ground = frames_to_success / float(avg_ground_goal_conditions) if success else -1
    record.append(frames_to_success_normalized_ground)
    
    # grasps
    left_grasp = demo["vr"]["vr_button_data"]["left_controller"][:, 0]
    right_grasp = demo["vr"]["vr_button_data"]["right_controller"][:, 0]
    
    left_grasp_engaged = left_grasp * (left_grasp > 0.8)
    right_grasp_engaged = right_grasp * (right_grasp > 0.8)
    
    left_grasp_on_filter = np.convolve(left_grasp_engaged, np.array([1, -1]))
    left_grasp_on = np.where(np.isclose(left_grasp_on_filter, 1, 0.2))
    
    right_grasp_on_filter = np.convolve(right_grasp_engaged, np.array([1, -1]))
    right_grasp_on = np.where(np.isclose(right_grasp_on_filter, 1, 0.2))
    
    record.append(np.size(left_grasp_on) + np.size(right_grasp_on))
    
    records.append(record)
    
success_plotting_data = pd.DataFrame.from_records(records, columns=columns)
success_plotting_data["task_label"] = success_plotting_data["task_name"] + "_" + success_plotting_data["task_instance"].astype(str)
success_plotting_data_nofailure = success_plotting_data[success_plotting_data["success"] == 1]
# -

# ### Total frames to reach success ONLY FOR SUCCESSFUL DEMOS - randomly selected scene

# randomly select scenes for some (task, task_id)
choice_fn = lambda obj: obj.loc[np.random.choice(obj.index), :]
success_data_randomscenes = success_plotting_data_nofailure.groupby(["task_name", "task_instance"], as_index=False).apply(choice_fn)

fig = plt.figure()
ax = sns.barplot(
    x="task_label",
    y="frames_to_success",
    data=success_data_randomscenes
)
plt.xticks(rotation=90)
plt.savefig('frames_to_success_randomscenes.pdf')

# ### Total frames to reach success ONLY FOR SUCCESSFUL DEMOS - average across scenes 

# average distances across different scenes 
success_data_avg = success_plotting_data_nofailure.groupby(['task_name', 'task_instance'], as_index=False).agg(np.mean)
success_data_avg["task_label"] = success_data_avg["task_name"] + "_" + success_data_avg["task_instance"].astype(str)

# +
fig = plt.figure()
ax = sns.barplot(
    x="task_label",
    y="frames_to_success",
    data=success_data_avg)

plt.xticks(rotation=90)
plt.savefig('frames_to_success_avgacrossscenes.pdf')

# +
# average across scenes for some (task, task_id)
success_plotting_data_nofailure = success_plotting_data[success_plotting_data["success"] == 1]

success_data_avgacrossscenes = success_plotting_data_nofailure.groupby(['task_name', 'task_instance'], as_index=False).agg(np.mean)
# -

# ### Total frames to reach success ONLY FOR SUCCESSFUL DEMOS - range

fig = plt.figure()
ax = sns.violinplot(
    x="task_label",
    y="frames_to_success",
    data=success_plotting_data_nofailure
)
plt.xticks(rotation=90)
plt.savefig('frames_to_success_range.pdf')

# # Time to success, normalized by num ground goal conditions

# ### Total frames to reach success ONLY FOR SUCCESSFUL DEMOS - average, normalized by num ground goal conditions

# +
fig = plt.figure()
ax = sns.barplot(
    x="task_label",
    y="frames_to_success_normalized_ground",
    data=success_data_avg)

plt.xticks(rotation=90)
plt.savefig('frames_to_success_avgacrossscenes.pdf')
# -

# # Correlation of grasps + time to reach success

# ### Total grasps vs. frames to success

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 8))
sns.regplot(
    x="frames_to_success",
    y="total_grasps",
    data=success_plotting_data_nofailure,
    ax=ax1
)
sns.regplot(
    x="frames_to_success_normalized_goal",
    y="total_grasps",
    data=success_plotting_data_nofailure,
    ax=ax2
)
sns.regplot(
    x="frames_to_success_normalized_ground",
    y="total_grasps",
    data=success_plotting_data_nofailure,
    ax=ax3
)


# # Failure rates

# ### Failure rate by task, scene_id 

task_label_success_data = success_plotting_data[["task_label", "success"]].groupby("task_label", as_index=False).agg(np.mean)
scene_id_success_data = success_plotting_data[["scene_id", "success"]].groupby("scene_id", as_index=False).agg(np.mean)

# +
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
sns.barplot(
    x="task_label",
    y="success",
    data=task_label_success_data,
    ax=ax1
)
# plt.xticks(rotation=90)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)

sns.barplot(
    x="scene_id",
    y="success",
    data=scene_id_success_data,
    ax=ax2
)
# plt.xticks(rotation=90)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)

# -


