import h5py
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd 
import seaborn as sns
import pprint
import matplotlib as mpl
from PIL import Image
from matplotlib import gridspec
from matplotlib.lines import Line2D

demo_file = '../iGibson/demos/packing_lunches_filtered/packing_lunches_filtered_1_Wainscott_0_int_success/packing_lunches_filtered_1_Wainscott_0_int_2021-03-16_13-49-10.hdf5'
demo = h5py.File(demo_file, 'r')
task = demo.attrs['/metadata/task_instance']
start_idx = max(
    min(np.where(demo['vr']['vr_event_data']['left_controller'])[0]),
    min(np.where(demo['vr']['vr_event_data']['right_controller'])[0])
)
selected_colors = ['#D81B60', '#1E88E5', '#FFC107', '#004D40']
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

fig = plt.figure(figsize=(16, 9), dpi=200)
idx = 0
gs  = gridspec.GridSpec(20, 20)
ax0 = plt.subplot(gs[0:16, :])
ax1 = plt.subplot(gs[17:19, 2:18])
ax2 = plt.subplot(gs[19, 2:18])
ax0.axis('off')
cmap = mpl.colors.ListedColormap(colors)

norm = mpl.colors.BoundaryNorm(boundaries, cmap.N)
cb = plt.colorbar(
    mpl.cm.ScalarMappable(cmap=cmap, norm=norm),
    cax=ax1,
    boundaries=boundaries,  # Adding values for extensions.
#         ticks=boundaries,
    ticks=[],
    spacing='proportional',
    orientation='horizontal',
    #use_gridspec=True,
)


legend_elements = [
    Line2D([0], [0], color=str(selected_colors[0]), lw=20, label='   Nav. w/o objs'),
    Line2D([0], [0], color=str(selected_colors[1]), lw=20, label='   Grasp'),
    Line2D([0], [0], color=str(selected_colors[2]), lw=20, label='   Nav. w/ objs'),
    Line2D([0], [0], color=str(selected_colors[3]), lw=20, label='   Release'),
]

ax2.axis('off')
ax2.legend(handles = legend_elements, loc='center', ncol=4, mode ='expand', fontsize = 12, frameon=False)

for frame in range(end_idx-start_idx):
    ax0.clear()
    ax0.imshow(Image.open('../iGibson/frame_out_path/{:05d}.jpg'.format(idx+start_idx)))
    ax0.axis('off')

    handle = ax1.annotate('',
                xy=(idx, 2000), xycoords='data',
                xytext=(idx, 2050), textcoords='data',
                arrowprops=dict(facecolor='black', arrowstyle='Simple, head_width=2, head_length=2'),
                horizontalalignment='right', verticalalignment='top')

    fig.savefig('out_frames/{:05d}.jpeg'.format(idx))
    handle.remove()
    idx += 1
