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
import matplotlib as mpl
from pathlib import *


sns.set_context("paper")

scene_id = 'Wainscott_0_int'

# demos_filepath = os.path.join('/cvgl2/u/chengshu/TaskNet/data/Rs_int_demos')
files = list(Path("d:/new_demo_data").rglob('*.hdf5'))


raw_data = []
demo_files = []
# for demo_file in os.listdir(demos_filepath):
for demo_file in files: 
    if ".hdf5" not in str(demo_file): 
        continue
    if scene_id not in str(demo_file):
        continue
    raw_data.append(h5py.File(str(demo_file), "r"))
    demo_files.append(str(demo_file))
    
def convert_name(name):
    if name == "assembling_gift_baskets_filtered":
        return "gift baskets"
    elif name == "organizing_school_stuff_filtered":
        return "school stuff"
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



print(raw_data)



# -


trav_map_resolution = 0.01
trav_map_size = 1000
def world_to_map(xy):
    world_xy = xy / trav_map_resolution
    world_xy[:, 1] *= -1
    return np.flip((world_xy + trav_map_size / 2.0)).astype(np.int)


# +
plt.figure(figsize=(20,20))
skip = 5

# floorplan_file = '/cvgl2/u/chengshu/TaskNet/data/floorplan/{}.png'.format(scene_id)
floorplan_file = f"c:/Users/igibs/TaskNet/data/floorplan/{scene_id}.png"
floorplan = plt.imread(floorplan_file)
colors = ['#004D40', '#D81B60', '#FFC107', '#1E88E5', '#FE6100']
task_done = set()
idx = 0
for i, (demo, demo_file) in enumerate(zip(raw_data[::-1], demo_files[::-1])):
    task_id = demo_file[:(demo_file.index(scene_id) - 1)]
    if task_id == 're-shelving_library_books_filtered_0':
        continue
    task = task_id[:-2]
    task = convert_name(task)
    if task in task_done:
        continue
    task_done.add(task)
    start_idx = max(
        min(np.where(demo['vr']['vr_event_data']['left_controller'])[0]),
        min(np.where(demo['vr']['vr_event_data']['right_controller'])[0])
    )

    satisfied = demo["goal_status"]["satisfied"]
    total_frames, total_goal_conds = satisfied.shape
    satisfied_goal_conds_by_frame = np.sum(satisfied, axis=1)
    success_trace = np.nonzero(satisfied_goal_conds_by_frame == float(total_goal_conds))[0]
#     print(success_trace)
    success = bool(len(success_trace))

    if success:
        print(success_trace)
        end_idx = np.min(success_trace) + 1
    else:
        end_idx = total_frames


    left_position = demo["vr"]["vr_device_data"]["left_controller"][start_idx:end_idx, 1:4]
    right_position = demo["vr"]["vr_device_data"]["right_controller"][start_idx:end_idx, 1:4]
    body_position = demo["vr"]["vr_device_data"]["vr_position_data"][start_idx:end_idx, 0:3]
    body_position_xy = body_position[:, 0:2]
    body_position_xy_map = world_to_map(body_position_xy)
    
    c = colors[idx % len(colors)]
    plt.plot(body_position_xy_map[:, 1], body_position_xy_map[:, 0], marker='o', linewidth=10, alpha=1.0, label=task, c=c)
    idx += 1

plt.axis('off')
plt.legend(fontsize=30, loc='lower left', bbox_to_anchor=(0.07, 0.06))
plt.imshow(floorplan)
plt.savefig('task_heatmap_{}.pdf'.format(scene_id), bbox_inches='tight', pad_inches=0, transparent=True)

<<<<<<< HEAD
print(raw_data)

=======
>>>>>>> 9bdc40d3b5efa06dbc5a1f47d8471ab509c01114

# +
# demos_filepath = os.path.join('/cvgl2/u/chengshu/TaskNet/data/examples_pre_hand')
demos_filepath = f"c:/Users/igibs/TaskNet/data/examples_pre_hand"


raw_data = []
demo_files = []
for demo_file in os.listdir(demos_filepath):
    if ".hdf5" not in demo_file: 
        continue
    if scene_id not in demo_file:
        continue
    raw_data.append(h5py.File(os.path.join(demos_filepath, demo_file), "r"))
    demo_files.append(demo_file)
# -

plt.clf()
selected_colors = ['#D81B60', '#1E88E5', '#FFC107', '#004D40']
print(raw_data)
print(demo_files)
for i, (demo, demo_file) in enumerate(zip(raw_data, demo_files)):
    print(i)
    task = demo_file[:(demo_file.index(scene_id) - 1)]
    if task != 'packing_lunches_1':
        continue
    start_idx = max(
        min(np.where(demo['vr']['vr_event_data']['left_controller'])[0]),
        min(np.where(demo['vr']['vr_event_data']['right_controller'])[0])
    )

    satisfied = demo["goal_status"]["satisfied"]
    total_frames, total_goal_conds = satisfied.shape
    satisfied_goal_conds_by_frame = np.sum(satisfied, axis=1)
    success_trace = np.nonzero(satisfied_goal_conds_by_frame == float(total_goal_conds))
    success = bool(len(success_trace))

    if success:
        end_idx = np.min(success_trace)
    else:
        end_idx = total_frames

    left_grasp = demo["vr"]["vr_button_data"]["left_controller"][start_idx:end_idx, 0]
    right_grasp = demo["vr"]["vr_button_data"]["right_controller"][start_idx:end_idx, 0]
    satisfied_goal_conds_by_frame = satisfied_goal_conds_by_frame[start_idx:end_idx]
    left_grasp_engaged = left_grasp > 0.8
    right_grasp_engaged = right_grasp > 0.8
    any_grasp_engaged = np.any([left_grasp_engaged, right_grasp_engaged], axis=0)

    phase = []
    bounds = []
    grasp = False
    transition = False
    transition_period = 0
    transition_max_length = 10
    prev_val = None
    prev_goal_cond = satisfied_goal_conds_by_frame[0]
    goal_progress = []
    for i in range(any_grasp_engaged.shape[0]):
        if not grasp and any_grasp_engaged[i]:
            grasp = True
            transition = True
        elif grasp and not any_grasp_engaged[i]:
            grasp = False
            transition = True
            
        if not grasp and not transition:
            cur_val = 0
        elif grasp and transition:
            cur_val = 1
        elif grasp and not transition:
            cur_val = 2
        elif not grasp and transition:
            cur_val = 3
        
        phase.append(cur_val)
        if prev_val is None or cur_val != prev_val:
            bounds.append((i, cur_val))
        prev_val = cur_val

        if transition:
            transition_period += 1
        if transition_period == transition_max_length:
            transition = False
            transition_period = 0
        
        if satisfied_goal_conds_by_frame[i] != prev_goal_cond:
            goal_progress.append(i + start_idx)
            prev_goal_cond = satisfied_goal_conds_by_frame[i]
            print(prev_goal_cond)
    goal_progress.append(any_grasp_engaged.shape[0] + start_idx)
    

    boundaries = [item[0] for item in bounds] + [any_grasp_engaged.shape[0]]
    colors = [selected_colors[item[1]] for item in bounds]

    fig, ax = plt.subplots(figsize=(60, 10))
    fig.subplots_adjust(bottom=0.5)

    cmap = mpl.colors.ListedColormap(colors)

    norm = mpl.colors.BoundaryNorm(boundaries, cmap.N)
    plt.colorbar(
        mpl.cm.ScalarMappable(cmap=cmap, norm=norm),
        cax=ax,
        boundaries=boundaries,  # Adding values for extensions.
#         ticks=boundaries,
        ticks=[],
        spacing='proportional',
        orientation='horizontal',
    )
    print(goal_progress)
    plt.savefig('task_seg_{}.png'.format(task))
    plt.show()
    print('task_seg_{}.png'.format(task))
    plt.clf()


<<<<<<< HEAD

=======
# +
demos_filepath = os.path.join('/cvgl2/u/chengshu/TaskNet/data/Beechwood_0_int_demos')

raw_data = []
demo_files = []
for demo_file in sorted(os.listdir(demos_filepath)):
    if ".hdf5" not in demo_file: 
        continue
    if scene_id not in demo_file:
        continue
    raw_data.append(h5py.File(os.path.join(demos_filepath, demo_file), "r"))
    demo_files.append(demo_file)
# -

trav_map_resolution = 0.01
trav_map_size = 2400
def world_to_map(xy):
    world_xy = xy / trav_map_resolution
    world_xy[:, 1] *= -1
    return np.flip((world_xy + trav_map_size / 2.0)).astype(np.int)


# +
scene_id = 'Beechwood_0_int'

plt.figure(figsize=(20,20))
skip = 5

floorplan_file = '/cvgl2/u/chengshu/TaskNet/data/floorplan/{}.png'.format(scene_id)
floorplan = plt.imread(floorplan_file)
colors = ['#004D40', '#D81B60', '#FFC107', '#1E88E5', '#FE6100', '#9CD4F3', '#1DD21D', '#5D3A9B']
task_done = set()
idx = 0
for i, (demo, demo_file) in enumerate(zip(raw_data[::-1], demo_files[::-1])):
    task_id = demo_file[:(demo_file.index(scene_id) - 1)]
    if task_id == 're-shelving_library_books_filtered_0':
        continue
    task = task_id[:-2]
    task = convert_name(task)
    if task in task_done:
        continue
    task_done.add(task)

    start_idx = max(
        min(np.where(demo['vr']['vr_event_data']['left_controller'])[0]),
        min(np.where(demo['vr']['vr_event_data']['right_controller'])[0])
    )

    satisfied = demo["goal_status"]["satisfied"]
    total_frames, total_goal_conds = satisfied.shape
    satisfied_goal_conds_by_frame = np.sum(satisfied, axis=1)
    success_trace = np.nonzero(satisfied_goal_conds_by_frame == float(total_goal_conds))
    success = bool(len(success_trace))

    if success:
        end_idx = np.min(success_trace)
    else:
        end_idx = total_frames


    left_position = demo["vr"]["vr_device_data"]["left_controller"][start_idx:end_idx, 1:4]
    right_position = demo["vr"]["vr_device_data"]["right_controller"][start_idx:end_idx, 1:4]
    body_position = demo["vr"]["vr_device_data"]["vr_position_data"][start_idx:end_idx, 0:3]
    body_position_xy = body_position[:, 0:2]
    body_position_xy_map = world_to_map(body_position_xy)
    
    c = colors[idx % len(colors)]
    plt.plot(body_position_xy_map[:, 1], body_position_xy_map[:, 0], marker='o', linewidth=5, alpha=1.0, label=task, c=c)
    idx += 1

plt.axis('off')
plt.legend(fontsize=18, loc='upper left', bbox_to_anchor=(0.02, 0.77))
plt.imshow(floorplan)
plt.savefig('task_heatmap_{}.pdf'.format(scene_id), bbox_inches='tight', pad_inches=0, transparent=True)
>>>>>>> 9bdc40d3b5efa06dbc5a1f47d8471ab509c01114
