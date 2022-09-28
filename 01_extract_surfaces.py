# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 08:39:28 2022

@author: firo
"""

import xarray as xr
import os
from skimage import measure
import trimesh
import numpy as np
from joblib import delayed, Parallel
import socket
from scipy import ndimage
host = socket.gethostname()


# TODO: add GPU support once cucim/cupy allow GPU marching cubes
# TODO: already allow cupy for matrix operations and loading
temp_folder = None
if host == 'DDM06609':
    temp_folder = r"Z:\users\firo\joblib_tmp"


class mesh_maker:
    def __init__(self,
                 nc_path = None,
                 out_path = None,
                 ref_timestep = 50,
                 timesteps = None, #'all', or array
                 z_boundaries = (0,-1),
                 use_gpu = False, #stub to call either cupy/cucim or not,
                 cpu_parallel = True,
                 njobs = 8,
                 ):
        self.nc_path = nc_path
        self.out_path = out_path
            
        self.zbot =  z_boundaries[0]
        self.ztop = z_boundaries[1]
        self.ref_ts = ref_timestep
        self.timesteps = timesteps
        self.use_gpu = use_gpu
        self.parallel = cpu_parallel
        self.njobs = njobs
    
    def load_data(self):
        self.dyn_data = xr.open_dataset(self.nc_path)
        if 'transition_matrix' in list(self.dyn_data.keys()):
            self.watermask = (self.dyn_data['transition_matrix']>0).data[:,:,self.zbot:self.ztop]
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

        
    def time_step_stl(self, ts):
        
        water = self.dyn_data['transition_matrix']<ts
        water = np.bitwise_and(water[:,:,self.zbot:self.ztop], self.watermask)
        
        if np.any(water):
            water[:,:,:2] = 0
            water[:,:,-3:] = 0
            verts, faces, _, _ = measure.marching_cubes(water.data) #_lewiner
            watermesh = trimesh.Trimesh(vertices = verts, faces = faces)    
            stl = trimesh.exchange.stl.export_stl_ascii(watermesh)
            stlpath = os.path.join(self.out_path, ''.join(['water_ts_',f'{ts:05}','.stl']))
            
            with open(stlpath, 'w+') as file: 
                 file.write(stl) 
                 
    def time_4D_stl(self, ts, phase=1, phasename = 'phase_1', clean=False):
        
        im = self.dyn_data['segmented'].sel(time=ts)==phase
        
        if clean: im = ndimage.binary_opening(im)
        
        if np.any(im):
            im[:,:,:2] = 0
            im[:,:,-3:] = 0
            verts, faces, _, _ = measure.marching_cubes(im.data) #_lewiner
            mesh = trimesh.Trimesh(vertices = verts, faces = faces)
            stl = trimesh.exchange.stl.export_stl_ascii(mesh)
            stlpath = os.path.join(self.out_path, ''.join([phasename, f'{ts:05}','.stl']))
            with open(stlpath, 'w+') as file: 
                 file.write(stl)            
            
            
    def run(self):
        # laod the data
        self.load_data()
       # TODO:close ncfile if error
        # make reference time step stl
        try:
            self.time_step_stl(self.ref_ts)
            
            # make all the other stls if called
            if self.timesteps is not None:
                if self.timesteps == 'all':
                    steps = np.arange(len(self.dyn_data['time']))
                else:
                    steps = self.timesteps
                
                if self.parallel:
                    Parallel(n_jobs=self.njobs, temp_folder=temp_folder)(delayed(self.time_step_stl)(ts) for ts in steps)
                else:
                    for ts in steps:
                        if not ts == self.ref_ts:
                            self.time_step_stl(ts)
        except Exception as e:
            print(e)
            self.dyn_data.close()
        self.dyn_data.close()
        
    def run2(self, phase, name, clean):
        # laod the data
        self.load_data()
       # TODO:close ncfile if error
        # make reference time step stl
        try:
            self.time_4D_stl(self.ref_ts, phase, name)
            
            # make all the other stls if called
            if self.timesteps is not None:
                if self.timesteps == 'all':
                    steps = np.arange(len(self.dyn_data['time']))
                else:
                    steps = self.timesteps
                
                if self.parallel:
                    Parallel(n_jobs=self.njobs, temp_folder=temp_folder)(delayed(self.time_4D_stl)(ts, phase, name, clean) for ts in steps)
                else:
                    for ts in steps:
                        if not ts == self.ref_ts:
                            self.time_4D_stl(ts)
        except Exception as e:
            print(e)
            self.dyn_data.close()
        self.dyn_data.close()
        
                    
    

        

            
        
        
        
