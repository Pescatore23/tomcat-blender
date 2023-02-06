# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 08:39:28 2022

@author: firo
"""

import xarray as xr
import os
from skimage import measure
from skimage import morphology 
from skimage.morphology import ball
import trimesh
import numpy as np
from joblib import delayed, Parallel
import socket
from scipy import ndimage
host = socket.gethostname()



# TODO: make this more elegant
try:
    import cupy as cp
    import cucim
    GPU_avail = True
except:
    print('cupy and cucim not found')
    GPU_avail = False


# TODO: add GPU support once cucim/cupy allow GPU marching cubes
# TODO: already allow cupy for matrix operations and loading, image cleaning already possible with GPU
temp_folder = None
if host == 'DDM06609':
    temp_folder = r"Z:\users\firo\joblib_tmp"
    
num_GPU = 1
if host == 'mpc2959.psi.ch':
    num_GPU = 5
    
    

def clean_binary_image(im, clean = True, remove_small=True,  minsize = 200, fp_radius = 1, i=0, GPU = True, GPU_avail=GPU_avail):
    # GPU?
    if clean or remove_small:
        if GPU and GPU_avail:
            gpu_id = i%num_GPU #use gpus 1 through 4, leaving the big A40 (0) alone or i%5 to use all 5
    
            with cp.cuda.Device(gpu_id):
                im = cp.array(im)
                if clean: im = cucim.skimage.morphology.binary_opening(im, footprint=cucim.skimage.morphology.ball(fp_radius))
                if remove_small: im = cucim.skimage.morphology.remove_small_objects(im, min_size=minsize)
                im = cp.asnumpy(im)
                mempool = cp.get_default_memory_pool()
                mempool.free_all_blocks()
            
        else: 
            if clean: im = ndimage.binary_opening(im, structure=ball(fp_radius))
            if remove_small: im = morphology.remove_small_objects(im, min_size=minsize)
        
    return im


class mesh_maker:
    def __init__(self,
                 nc_path = None,
                 out_path = None,
                 ref_timestep = 50,
                 timesteps = None, #'all', or array
                 x_boundaries = (0,-1),
                 y_boundaries = (0,-1),
                 z_boundaries = (0,-1),
                 use_gpu = False, #stub to call either cupy/cucim or not,
                 cpu_parallel = True,
                 njobs = 16,
                 GPU = True
                 ):
        self.nc_path = nc_path
        self.out_path = out_path
            
        self.xbot = x_boundaries[0]
        self.xtop = x_boundaries[1]
        self.ybot = y_boundaries[0]
        self.ytop = y_boundaries[1]
        self.zbot = z_boundaries[0]
        self.ztop = z_boundaries[1]
        
        self.ref_ts = ref_timestep
        self.timesteps = timesteps
        self.use_gpu = use_gpu
        self.parallel = cpu_parallel
        self.njobs = njobs
        self.GPU = GPU
    
    def load_data(self):
        self.dyn_data = xr.open_dataset(self.nc_path)
        if 'transition_matrix' in list(self.dyn_data.keys()):
            self.watermask = (self.dyn_data['transition_matrix']>0).data[self.xbot:self.xtop,self.ybot:self.ytop,self.zbot:self.ztop]
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

        
    def time_step_stl(self, ts):
        
        water = self.dyn_data['transition_matrix']<ts
        water = np.bitwise_and(water[self.xbot:self.xtop,self.ybot:self.ytop,self.zbot:self.ztop], self.watermask)
        
        if np.any(water):
            water[:,:,:2] = 0
            water[:,:,-3:] = 0
            verts, faces, _, _ = measure.marching_cubes(water.data) #_lewiner
            watermesh = trimesh.Trimesh(vertices = verts, faces = faces)    
            stl = trimesh.exchange.stl.export_stl_ascii(watermesh)
            stlpath = os.path.join(self.out_path, ''.join(['water_ts_',f'{ts:05}','.stl']))
            
            with open(stlpath, 'w+') as file: 
                 file.write(stl) 
                 
    def time_4D_stl(self, ts, phase=1, phasename = 'phase_1', clean=False, remove_small= False, fp_radius = 1, minsize=20):
        
        im = self.dyn_data['segmented'].sel(time=ts)[self.xbot:self.xtop,self.ybot:self.ytop,self.zbot:self.ztop]==phase
        
        if np.any(im):
            im = im.data
            # TODO: use GPU
            # if clean: im = ndimage.binary_opening(im, structure=fp)
            # if remove_small: im = morphology.remove_small_objects(im, min_size=minsize)
            
            #crop boundaries
            im[:,:2,:] = 0
            im[:,-3:,:] = 0
            im[:2,:,:] = 0
            im[-3:,:,:] = 0
            im[:,:,:2] = 0
            im[:,:,-3:] = 0
            
            im = clean_binary_image(im, clean, remove_small,  minsize, fp_radius, i=ts, GPU = self.GPU)
                        
            verts, faces, _, _ = measure.marching_cubes(im) #_lewiner
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
        
    def run2(self, phase, name, clean=False, remove_small=False, fp_radius=1, minsize=20):
        # laod the data
        self.load_data()
       # TODO:close ncfile if error
        # make reference time step stl
        try:
            self.time_4D_stl(self.ref_ts, phase, name, clean)
            
            # make all the other stls if called
            if self.timesteps is not None:
                if self.timesteps == 'all':
                    steps = np.arange(len(self.dyn_data['time']))
                else:
                    steps = self.timesteps
                
                if self.parallel:
                    Parallel(n_jobs=self.njobs, temp_folder=temp_folder)(delayed(self.time_4D_stl)(ts, phase, name, clean,remove_small, fp_radius, minsize) for ts in steps)
                else:
                    for ts in steps:
                        if not ts == self.ref_ts:
                            self.time_4D_stl(ts, phase, name, clean)
        except Exception as e:
            print(e)
            self.dyn_data.close()
        self.dyn_data.close()
        
                    
    

        

            
        
        
        
