# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 10:09:42 2022

converts time steps into real time

@author: firo
"""

import xarray as xr
import os
import numpy as np
import shutil

nc_path = r"Z:\Robert_TOMCAT_3_combined_archives\unmasked\dyn_data_T3_025_3_III.nc"

timestep_folder = r"Z:\anim_test_full_png_int"
time_folder = r"R:\Scratch\305\_Robert\time_test"

if not os.path.exists(time_folder):
    os.makedir(time_folder)

fileprefix = 'water_ts_'
pfx = len(fileprefix)

filesuffix = '.png'
sfx = len(filesuffix)

dyn_data = xr.open_dataset(nc_path)
exp_time = dyn_data['time'].data
dyn_data.close()


# temporary solution: manually define time steps and framerate

def move_file(ts, folder):
    filename = ''.join([fileprefix,f'{ts:05}', filesuffix])
    filepath = os.path.join(timestep_folder, filename)
    if os.path.exists(filepath):
        shutil.move(filepath, os.path.join(folder,filename))

# part1 6s per scan
# part1_steps = np.arange(101)

# part1_folder = os.path.join(timestep_folder, 'part1')
# if not os.path.exists(part1_folder):
#     os.mkdir(part1_folder)

# for ts in part1_steps:
#     move_file(ts, part1_folder)
    
# # part2 1s per scan
# part2_steps = np.arange(101,220)
# part2_folder = os.path.join(timestep_folder, 'part2')
# if not os.path.exists(part2_folder):
#     os.mkdir(part2_folder)
# for ts in part2_steps:
#     move_file(ts, part2_folder)

# # part3 7s per scan
# part3_steps = np.arange(220, len(exp_time))
# part3_folder = os.path.join(timestep_folder, 'part3')
# if not os.path.exists(part3_folder):
#     os.mkdir(part3_folder)
# for ts in part3_steps:
#     move_file(ts, part3_folder)

# part1 0.4s per scan
part1_steps = np.arange(180)
part1_folder = os.path.join(timestep_folder, 'part1')
if not os.path.exists(part1_folder):
    os.mkdir(part1_folder)

for ts in part1_steps:
    move_file(ts, part1_folder)
    
# part2 0.8s per scan
part2_steps = np.arange(180,271)
part2_folder = os.path.join(timestep_folder, 'part2')
if not os.path.exists(part2_folder):
    os.mkdir(part2_folder)
for ts in part2_steps:
    move_file(ts, part2_folder)
    
