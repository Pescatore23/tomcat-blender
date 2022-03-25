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

timestep_folder = r"Z:\anim_test_full_png"
time_folder = r"R:\Scratch\305\_Robert\time_test"

if not os.path.exists(time_folder):
    os.makedir(time_folder)

fileprefix = 'water_'
pfx = len(fileprefix)

filesuffix = '.png'
sfx = len(filesuffix)

time_array = np.arange(0,1600,1) #s

dyn_data = xr.open_dataset(nc_path)
exp_time = dyn_data['time'].data
dyn_data.close()

for t in time_array:
    ts = np.argmax(exp_time>t)-1
    
    step_file = ''.join([fileprefix,str(ts),filesuffix])
    prev_step_file = ''.join([fileprefix,str(ts-1),filesuffix])
    
    step_path = os.path.join(timestep_folder, step_file)
    prev_path = os.path.join(timestep_folder, prev_step_file)
    
    time_file = ''.join(['{:.2f}'.format(t),'_s.png'])
    time_path = os.path.join(time_folder, time_file)
    
    if os.path.exists(step_path):
        shutil.copyfile(step_path, time_path )
    
    # TODO: allow to go back more than one step ; probably unnecessary, noise should cause all time steps to render
    elif os.path.exists(prev_path):
        shutil.copyfile(prev_path, time_path )
    
    
    
