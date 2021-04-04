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
from pathlib import *

sns.set_context("paper")
selected_colors = ['#D81B60', '#1E88E5', '#FFC107', '#004D40']
our_palette = sns.color_palette(selected_colors)
sns.set_palette(our_palette)

# demos_filepath = os.path.join("d:", "external_demos_data")
# raw_data = []
# for demo_file in os.listdir(demos_filepath):
#     if "mp4" in demo_file: 
#         continue
#     raw_data.append(h5py.File(os.path.join(demos_filepath, demo_file), "r"))

files = list(Path("d:/new_demo_data").rglob('*.hdf5'))
good_files = []
bad_files = []
raw_data = []
for file in files:
#     print(str(file))
    if "OLD" in str(file):
        bad_files.append(file)
        continue
    f = h5py.File(file, 'r')
    if min(np.sum(f['goal_status']['unsatisfied'], axis=1)) != 0:
        bad_files.append(file)
        continue
    if "cleaning_out_drawers_filtered_0_Wainscott" in str(file) and '16-10-50' in str(file):
        bad_files.append(file)
        continue
    if "organizing_school_stuff_filtered_0_Pomaria_1_int_2021-03-15_17-24-01" in str(file):
        bad_files.append(file)
        continue
    good_files.append(file)
    raw_data.append(f)
print(len(raw_data))

    
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
    elif name == "putting_dishes_away_after_cleaning_filtered":
        return "dishes"
    elif name == "putting_away_Christmas_decorations_filtered":
        return "decorations"
    elif name == "re-shelving_library_books_filtered":
        return "books"
    else:
        return name


# -


# # Distance, Work

# +
records = []
columns = [
    "task_name",
    "task_instance",
    "scene_id",
    "left_total_dist",
    "right_total_dist",
    "body_total_dist",
    "left_total_force",
    "right_total_force",
    "body_total_force",
    "left_total_work",
    "right_total_work",
    "body_total_work",
    "all_devices_total_work"
]

clip = .2

for demo in raw_data: 
    record = []
    record.append(convert_name(demo.attrs["/metadata/task_name"]))
    record.append(demo.attrs["/metadata/task_instance"])
    record.append(demo.attrs["/metadata/scene_id"][:-4])
    
    # frame boundaries 
    start_idx = max(min(np.where(demo['vr']['vr_event_data']['left_controller'])[0]), min(np.where(demo['vr']['vr_event_data']['right_controller'])[0]))
    start_idx += 50
    satisfied = demo["goal_status"]["satisfied"]
    total_frames, total_goal_conds = satisfied.shape
    satisfied_goal_conds_by_frame = np.sum(satisfied, axis=1)
    success_trace = np.nonzero(satisfied_goal_conds_by_frame == float(total_goal_conds))
    success = bool(len(success_trace))
    if success:
        end_idx = np.min(success_trace) + 1
    else:
        end_idx = total_frames
    
    # total distance 
    left_position = demo["vr"]["vr_device_data"]["left_controller"][start_idx:end_idx, 1:4]
    right_position = demo["vr"]["vr_device_data"]["right_controller"][start_idx:end_idx, 1:4]
    body_position = demo["vr"]["vr_device_data"]["vr_position_data"][start_idx:end_idx, 0:3]
    
    left_delta_position = np.linalg.norm(left_position[1:-1] - left_position[0:-2], axis=1)
    right_delta_position = np.linalg.norm(right_position[1:-1] - right_position[0:-2], axis=1)
    body_delta_position = np.linalg.norm(body_position[1:-1] - body_position[0:-2], axis=1)

    left_delta_position = np.clip(left_delta_position, -clip, clip)
    right_delta_position = np.clip(right_delta_position, -clip, clip)
    body_delta_position = np.clip(body_delta_position, -clip, clip)
    
    record.append(np.sum(left_delta_position))
    record.append(np.sum(right_delta_position))
    record.append(np.sum(body_delta_position))
    
    # work (only translational forces)
    left_force = demo['vr']['vr_device_data']['left_controller'][start_idx + 2:end_idx, 17:20]
    right_force = demo['vr']['vr_device_data']['right_controller'][start_idx + 2:end_idx, 17:20]
    body_force = demo['vr']['vr_device_data']['vr_position_data'][start_idx + 2:end_idx, 6:9]

    record.append(np.sum(left_force))
    record.append(np.sum(right_force))
    record.append(np.sum(body_force))
    
    left_force = np.linalg.norm(left_force, axis=1)
    right_force = np.linalg.norm(right_force, axis=1)
    body_force = np.linalg.norm(body_force, axis=1)

    left_work = left_delta_position * left_force
    right_work = right_delta_position * right_force
    body_work = body_delta_position * body_force
    
    left_total_work = np.sum(left_work)
    right_total_work = np.sum(right_work)
    body_total_work = np.sum(body_work)
    all_devices_total_work = left_total_work + right_total_work + body_total_work
    
    record.append(left_total_work)
    record.append(right_total_work)
    record.append(body_total_work)
    record.append(all_devices_total_work)
    
    records.append(record)
    

dist_plotting_data = pd.DataFrame.from_records(records, columns=columns)
dist_plotting_data["task_label"] = dist_plotting_data["task_name"] + "_" + dist_plotting_data["task_instance"].astype(str)

# -

# ### Total distance traveled by task - randomly selected scene

# +
# randomly select scenes for some (task, task_id)
choice_fn = lambda obj: obj.loc[np.random.choice(obj.index), :]
dist_data_randomscenes = dist_plotting_data.groupby(["task_label"], as_index=False).apply(choice_fn)

hued_dfs = [
    dist_data_randomscenes[["task_label", "left_total_dist"]].rename(columns={"left_total_dist": "total_dist"}),
    dist_data_randomscenes[["task_label", "right_total_dist"]].rename(columns={"right_total_dist": "total_dist"}),
    dist_data_randomscenes[["task_label", "body_total_dist"]].rename(columns={"body_total_dist": "total_dist"})
]
hued_dfs[0]["device"] = "left"
hued_dfs[1]["device"] = "right"
hued_dfs[2]["device"] = "body"

hued_dist_data_randomscenes = pd.concat(hued_dfs)
# -

fig = plt.figure(figsize=(10, 6))
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
dist_data_avg = dist_plotting_data.groupby(['task_label'], as_index=False).agg(np.mean)

hued_dfs = [
    dist_data_avg[["task_label", "left_total_dist"]].rename(columns={"left_total_dist": "total_dist"}),
    dist_data_avg[["task_label", "right_total_dist"]].rename(columns={"right_total_dist": "total_dist"}),
    dist_data_avg[["task_label", "body_total_dist"]].rename(columns={"body_total_dist": "total_dist"})
]
hued_dfs[0]["device"] = "left"
hued_dfs[1]["device"] = "right"
hued_dfs[2]["device"] = "body"

hued_dist_data_avg = pd.concat(hued_dfs)

# -

fig = plt.figure(figsize=(10, 6))
ax = sns.barplot(
    x="task_label",
    y="total_dist",
    hue="device",
    data=hued_dist_data_avg
)
plt.xticks(rotation=90)
plt.savefig('total_distance_avg.pdf')

# ### Total distance traveled by task - whisker plot across scenes 

# +
hued_dfs = [
    dist_plotting_data[["task_label", "left_total_dist"]].rename(columns={"left_total_dist": "total_dist"}),
    dist_plotting_data[["task_label", "right_total_dist"]].rename(columns={"right_total_dist": "total_dist"}),
    dist_plotting_data[["task_label", "body_total_dist"]].rename(columns={"body_total_dist": "total_dist"})
]
hued_dfs[0]["device"] = "left"
hued_dfs[1]["device"] = "right"
hued_dfs[2]["device"] = "body"

hued_plotting_data = pd.concat(hued_dfs)

# +
our_palette = sns.color_palette(selected_colors)

fig = plt.figure(figsize=(10, 6))
# ax = sns.stripplot(x="task_label", y="total_dist", data=hued_plotting_data, jitter=0.05)
ax = sns.boxplot(x="task_label", y="total_dist", hue="device", data=hued_plotting_data)
plt.xticks(rotation=90)
plt.savefig("total_distance_range.pdf")

fig = plt.figure(figsize=(10, 6))
ax1 = sns.boxplot(
    x="task_label", 
    y="body_total_dist", 
    data=dist_plotting_data, 
    palette=our_palette,
    order=dist_plotting_data.sort_values("task_label").task_label.drop_duplicates(),    
)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=60, ha="right", fontsize=15)
plt.title("Total distance traveled by body during each activity instance", fontsize=20)
plt.ylabel("Total distance traveled by body", fontsize=15)
plt.xlabel("Activity instance", fontsize=15)
plt.yticks(fontsize=15)
plt.savefig("body_total_distance_range.pdf", bbox_inches="tight")
# -


# ### Total work by task - avg across scenes

# +
# average distances across different scenes 
dist_data_avg = dist_plotting_data.groupby(['task_label'], as_index=False).agg(np.mean)

hued_dfs = [
    dist_data_avg[["task_label", "left_total_work"]].rename(columns={"left_total_work": "total_work"}),
    dist_data_avg[["task_label", "right_total_work"]].rename(columns={"right_total_work": "total_work"}),
    dist_data_avg[["task_label", "body_total_work"]].rename(columns={"body_total_work": "total_work"})
]
hued_dfs[0]["device"] = "left"
hued_dfs[1]["device"] = "right"
hued_dfs[2]["device"] = "body"

hued_dist_data_avg = pd.concat(hued_dfs)
# -

fig = plt.figure(figsize=(10, 6))
ax = sns.barplot(
    x="task_label",
    y="total_work",
    hue="device",
    data=hued_dist_data_avg
)
plt.xticks(rotation=90)
plt.savefig('total_work_avg.pdf')

# ### Total work by task - range across scenes

# +
hued_dfs = [
    dist_plotting_data[["task_label", "left_total_work"]].rename(columns={"left_total_work": "total_work"}),
    dist_plotting_data[["task_label", "right_total_work"]].rename(columns={"right_total_work": "total_work"}),
    dist_plotting_data[["task_label", "body_total_work"]].rename(columns={"body_total_work": "total_work"})
]
hued_dfs[0]["device"] = "left"
hued_dfs[1]["device"] = "right"
hued_dfs[2]["device"] = "body"

hued_plotting_data = pd.concat(hued_dfs)



# +
fig = plt.figure(figsize=(10, 6))
# ax = sns.stripplot(x="task_label", y="total_dist", data=hued_plotting_data, jitter=0.05)
ax = sns.boxplot(
    x="task_label", 
    y="total_work", 
    hue="device", 
    data=hued_plotting_data)
plt.xticks(rotation=90)
plt.savefig("total_work_range.pdf")

fig = plt.figure(figsize=(10, 6))
ax1 = sns.boxplot(
    x="task_label", 
    y="all_devices_total_work", 
    data=dist_plotting_data, 
    palette=our_palette,
    order=dist_plotting_data.sort_values("task_label").task_label.drop_duplicates(),
)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=60, ha="right", fontsize=15)
plt.yticks(fontsize=15)
plt.title("Total work done during each activity instance", fontsize=20)
plt.ylabel("Total work done by hands and body", fontsize=15)
plt.xlabel("Activity instance", fontsize=15)
plt.yticks(fontsize=15)
plt.savefig("devices_total_work_range.pdf", bbox_inches="tight")
# -

# # Time to success 

# +
import tasknet
from tasknet.task_base import TaskNetTask 
tasknet.set_backend("iGibson")

sns.set_palette(sns.color_palette(selected_colors))
our_palette = sns.color_palette(selected_colors)


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
    frames_to_success = np.min(success_trace) + 1 if success else -1
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

# +

fig = plt.figure(figsize=(10, 6))
ax = sns.barplot(
    x="task_label",
    y="frames_to_success",
    data=success_data_randomscenes,
    palette=our_palette
)
plt.xticks(rotation=90)
plt.savefig('frames_to_success_randomscenes.pdf')
# -

# ### Total frames to reach success ONLY FOR SUCCESSFUL DEMOS - average across scenes 

# average distances across different scenes 
success_data_avg = success_plotting_data_nofailure.groupby(['task_name', 'task_instance'], as_index=False).agg(np.mean)
success_data_avg["task_label"] = success_data_avg["task_name"] + "_" + success_data_avg["task_instance"].astype(str)

# +
fig = plt.figure(figsize=(10, 6))
ax = sns.barplot(
    x="task_label",
    y="frames_to_success",
    data=success_data_avg,
    palette=our_palette
)

plt.xticks(rotation=90)
plt.savefig('frames_to_success_avg.pdf')

# +
# average across scenes for some (task, task_id)
success_plotting_data_nofailure = success_plotting_data[success_plotting_data["success"] == 1]

success_data_avgacrossscenes = success_plotting_data_nofailure.groupby(['task_label'], as_index=False).agg(np.mean)
# -

# ### Total frames to reach success ONLY FOR SUCCESSFUL DEMOS - range

fig = plt.figure(figsize=(10, 6))
ax = sns.boxplot(
    x="task_label",
    y="frames_to_success",
    data=success_plotting_data_nofailure,
    palette=our_palette,
    order=success_plotting_data_nofailure.sort_values("task_label").task_label.drop_duplicates(),
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=60, ha="right", fontsize=15)
plt.yticks(fontsize=15)
plt.title("Frames elapsed until success", fontsize=20)
plt.ylabel("Frames success", fontsize=15)
plt.xlabel("Activity instance", fontsize=15)
plt.yticks(fontsize=15)
plt.savefig('frames_to_success_range.pdf', bbox_inches="tight")

# # Time to success, normalized by num ground goal conditions

# ### Total frames to reach success ONLY FOR SUCCESSFUL DEMOS - average, normalized by num ground goal conditions

# +
fig = plt.figure(figsize=(10, 6))
ax = sns.barplot(
    x="task_label",
    y="frames_to_success_normalized_ground",
    data=success_data_avg,
    palette=our_palette
)

plt.xticks(rotation=90)
plt.savefig('frames_to_success_avg_groundnorm.pdf')
# -

# ### Total frames to reach success ONLY FOR SUCCESSFUL DEMOS - range, normalized by num ground goal conditions

fig = plt.figure(figsize=(10, 6))
ax = sns.boxplot(
    x="task_label",
    y="frames_to_success_normalized_ground",
    data=success_plotting_data_nofailure,
    palette=our_palette,
    order=success_plotting_data_nofailure.sort_values("task_label").task_label.drop_duplicates(),
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=60, ha="right", fontsize=15)
plt.yticks(fontsize=15)
plt.title("Frames elapsed until success, normalized by activity volume", fontsize=20)
plt.ylabel("Frames to success / activity volume", fontsize=15)
plt.xlabel("Activity instance", fontsize=15)
plt.yticks(fontsize=15)
plt.savefig('frames_to_success_range_norm.pdf', bbox_inches="tight")

# # Correlation of task duration and efficiency

success_dist_plotting_data = pd.merge(dist_plotting_data, success_plotting_data_nofailure, on=["task_label", "scene_id"], how="inner")


# ### Frames to success vs. total work

# +
fig1 = plt.figure(figsize=(10, 8))
sns.regplot(
    x="right_total_work",
    y="frames_to_success",
    data=success_dist_plotting_data,
)
plt.savefig("duration_vs_right_work.pdf")


fig2 = plt.figure(figsize=(10, 8))
sns.regplot(
    x="body_total_work",
    y="frames_to_success",
    data=success_dist_plotting_data,
)
plt.savefig("duration_vs_body_work.pdf")
                  
fig3 = plt.figure(figsize=(10, 8))
sns.regplot(
    x="right_total_work",
    y="frames_to_success_normalized_ground",
    data=success_dist_plotting_data,
)
plt.savefig("normalized_duration_vs_right_work.pdf")


fig4 = plt.figure(figsize=(10, 8))
sns.regplot(
    x="body_total_work",
    y="frames_to_success_normalized_ground",
    data=success_dist_plotting_data,
)
plt.savefig("normalized_duration_vs_body_work.pdf")
                  
print()
print(success_dist_plotting_data["left_total_work"].corr(success_dist_plotting_data["frames_to_success"]))
print(success_dist_plotting_data["right_total_work"].corr(success_dist_plotting_data["frames_to_success"]))
print(success_dist_plotting_data["body_total_work"].corr(success_dist_plotting_data["frames_to_success"]))
print()
print(success_dist_plotting_data["left_total_work"].corr(success_dist_plotting_data["frames_to_success_normalized_ground"]))
print(success_dist_plotting_data["right_total_work"].corr(success_dist_plotting_data["frames_to_success_normalized_ground"]))
print(success_dist_plotting_data["body_total_work"].corr(success_dist_plotting_data["frames_to_success_normalized_ground"]))

print()
print('FORCE AND FRAMES TO SUCCESS') 
print(success_dist_plotting_data["left_total_force"].corr(success_dist_plotting_data["frames_to_success"]))
print(success_dist_plotting_data["left_total_force"].corr(success_dist_plotting_data["frames_to_success_normalized_ground"]))
# -

# # Correlation of grasps + work

# ### Total grasps vs. total work 

# +
fig, (ax2, ax3) = plt.subplots(1, 2, figsize=(20, 8))

# no normalization
# sns.regplot(
#     x="left_total_work",
#     y="total_grasps",
#     data=success_dist_plotting_data,
#     ax=ax1
# )
print(success_dist_plotting_data["left_total_work"].corr(success_dist_plotting_data["total_grasps"]))

sns.regplot(
    x="right_total_work",
    y="total_grasps",
    data=success_dist_plotting_data,
    ax=ax2
)
print(success_dist_plotting_data["right_total_work"].corr(success_dist_plotting_data["total_grasps"]))

sns.regplot(
    x="body_total_work",
    y="total_grasps",
    data=success_dist_plotting_data,
    ax=ax3
)
print(success_dist_plotting_data["body_total_work"].corr(success_dist_plotting_data["total_grasps"]))

plt.savefig("grasps_vs_work.pdf")

# -

# # Failure rates

# ### Failure rate by task, scene_id 

task_label_success_data = success_plotting_data[["task_label", "success"]].groupby("task_label", as_index=False).agg(np.mean)
scene_id_success_data = success_plotting_data[["scene_id", "success"]].groupby("scene_id", as_index=False).agg(np.mean)

# +
fig, plt.figure(figsize=(10, 6))
# sns.barplot(
#     x="task_label",
#     y="success",
#     data=task_label_success_data,
# )
ax = sns.barplot(
    x="task_label",
    y="success",
    data=task_label_success_data,
#     color="blue",
#     saturation=.5
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=60, ha="right", fontsize=15)
plt.yticks(fontsize=15)
plt.savefig("failure_rate_by_task.pdf", bbox_inches="tight")


fig, plt.figure(figsize=(10, 6))
ax1 = sns.barplot(
    x="scene_id",
    y="success",
    data=scene_id_success_data,
#     ax=ax2
)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=60, ha="right", fontsize=15)
plt.yticks(fontsize=15)
plt.savefig("failure_rate_by_scene.pdf", bbox_inches="tight")

# -

success_dist_plotting_data

# # Summary statistics

# +
success_dist_plotting_data["total_work"] = success_dist_plotting_data["left_total_work"] + \
                                           success_dist_plotting_data["right_total_work"] + \
                                           success_dist_plotting_data["body_total_work"]
# success_dist_plotting_data["total_dist"] = success_dist_plotting_data["left_total_dist"] + \
#                                            success_dist_plotting_data["right_total_dist"] + \
#                                            success_dist_plotting_data["body_total_dist"]
summary = success_dist_plotting_data.describe()
# summary

task_summaries = success_dist_plotting_data.groupby(["task_label"], as_index=False).agg([np.mean, np.std])
task_summaries = task_summaries[[("num_ground_goal_conditions", "mean"),
                                ("num_ground_goal_conditions", "std"),
                                ("total_work", "mean"),
                                ("total_work", "std"),
                                ("body_total_dist", "mean"),
                                ("body_total_dist", "std"),
                                ("frames_to_success", "mean"),
                                ("frames_to_success", "std")]]
#                                 "total_work", "body_total_distance", "frames_to_success"]
task_summaries.to_csv("task_summaries.csv")
task_summaries
# -

a = success_dist_plotting_data.groupby(["task_label"], as_index=False)["num_ground_goal_conditions"]
names = []
groups = []
for name, group in a:
    names.append(name)
    groups.append(group)
print(names)
groups[7]


