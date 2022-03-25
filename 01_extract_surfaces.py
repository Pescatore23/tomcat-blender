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


# TODO: add GPU support once cucim/cupy allow GPU marching cubes
# TODO: already allow cupy for matrix operations and loading


class mesh_maker:
    def __init__(self,
                 nc_path = None,
                 out_path = None,
                 ref_timestep = 50,
                 timesteps = None, #'all', or array
                 z_boundaries = (0,-1),
                 use_gpu = False, #stub to call either cupy/cucim or not,
                 ):
        self.nc_path = nc_path
        self.out_path = out_path
            
        self.zbot =  z_boundaries[0]
        self.ztop = z_boundaries[1]
        self.ref_ts = ref_timestep
        self.timesteps = timesteps
        self.use_gpu = use_gpu
    
    def load_data(self):
        self.dyn_data = xr.open_dataset(self.nc_path)
        self.watermask = (self.dyn_data['transition_matrix']>0).data[:,:,self.zbot:self.ztop]
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

        
    def time_step_stl(self, ts):
        
        water = self.dyn_data['transition_matrix']<ts
        water = np.bitwise_and(water[:,:,self.zbot:self.ztop], self.watermask)
        
        if np.any(water):
            water[:,:,:2] = 0
            water[:,:,-3:] = 0
            verts, faces, _, _ = measure.marching_cubes_lewiner(water.data)
            watermesh = trimesh.Trimesh(vertices = verts, faces = faces)    
            stl = trimesh.exchange.stl.export_stl_ascii(watermesh)
            stlpath = os.path.join(self.out_path, ''.join(['water_ts_',str(ts),'.stl']))
            
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
                if self.timesteps.any() == 'all':
                    steps = np.arange(len(self.dyn_data['time']))
                else:
                    steps = self.timesteps
                for ts in steps:
                    if not ts == self.ref_ts:
                        self.time_step_stl(ts)
        except Exception as e:
            print(e)
            self.dyn_data.close()
        self.dyn_data.close()
        
                    
    

        

            
        
        
        
