# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:37:40 2023

extracts numpy boolean array from nc and stores as npy
strips all metadata, but allows to process volume data within blender using pyopenvdb

@author: fische_r
"""

import xarray as xr
import os
from skimage import morphology 
from skimage.morphology import ball
import numpy as np
from joblib import delayed, Parallel
import socket
from scipy import ndimage
host = socket.gethostname()
import argparse

# TODO: make this more elegant
try:
    import cupy as cp
    import cucim
    GPU_avail = True
except:
    print("cupy or cucim not found, can't use GPU")
    GPU_avail = False

# default parameters

# TODO: add GPU support once cucim/cupy allow GPU marching cubes
# TODO: already allow cupy for matrix operations and loading, image cleaning already possible with GPU
temp_folder = None
 
num_GPU = 1
n_jobs = 4
if host == 'mpc2959.psi.ch':
    num_GPU = 5
    n_jobs = 16
    
    
    
class volume_maker:
    def __init__(self,
                 args = None):
        self.clean = args.clean_image
        self.remove_small = args.remove_small
        self.footprint = args.footprint
        self.ts = args.time_step
        self.minsize = args.minsize
        
        self.topoutfolder = args.output_path
        self.array_name = args.segmented_name
        self.ph = args.phase
        
    
        
    def clean_binary_image(self, im, clean = True, remove_small=True,  minsize = 200, fp_radius = 1, i=0, GPU = True, GPU_avail=GPU_avail):
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
    
    def xarray_to_npy(self, im, ts, i=0):
        im = im == self.ph
        im = self.clean_binary_image(im, i=i, clean = self.clean , remove_small=self.remove_small,  minsize = self.minsize, fp_radius = self.footprint)
        
        outpath = os.path.join(self.topoutfolder, self.array_name+'_phase_'+str(self.ph)+'_ts_'+f'{ts:04d}'+'.npy')
        np.save(outpath, im)
        
    def nc_to_set_of_npy(self):
        imdata = self.data[self.array_name]
        if self.ts<0:
            print('processing all time steps')
            timesteps = imdata.timestep.data
            length = len(timesteps)
             
            Parallel(n_jobs=n_jobs, temp_folder=temp_folder)(delayed(self.xarray_to_npy)(imdata.sel(timestep=timesteps[i]), timesteps[i], i) for i in range(length))
            
        else:
            print('processing time step ',str(self.ts))
            self.xarray_to_npy(imdata.sel(timestep=self.ts), self.ts)

if __name__ == '__main__':
    ### Parse arguments
    parser = argparse.ArgumentParser(description='preprocessing parameters')
    parser.add_argument('-o', '--output_path', type = str, default = '', help = 'path to folder that will contain the .npy files')
    parser.add_argument('-i', '--input_path', type=str, default='', help = 'path to the .nc-file containing the segmented data')
    parser.add_argument('-cl', '--clean_image', type = bool, default = True, help = 'wheter to remove spurious pixel by binaray opening')
    parser.add_argument('-fp', '--footprint', type = int, default = 1, help = 'radius of the sphere stencel used for the binary opening')
    parser.add_argument('-rs', '--remove_small', type = bool, default=True, help = 'wheter to remove objects smaller than minsize')
    parser.add_argument('-ms', '--minsize', type = int, default=20, help = 'minimum size of connected objects to keep')
    parser.add_argument('-ts', '--time_step', type = int, default=0, help = 'time step that is processed, -1 for all')
    parser.add_argument('-sn', '--segmented_name', type = str, default = 'segmented', help = 'name of the data array in the .nc')
    parser.add_argument('-ph', '--phase', type = int, default = 1, help='which phase to extract, -1 for all except 0 (not yet implemented)')
    
    args = parser.parse_args()
    
    VM = volume_maker(args)
    
    # lazy load the data
    VM.data = xr.open_dataset(args.input_path)
    
    #create outfolder if necessary
    if not os.path.exists(VM.topoutfolder):
        os.mkdir(VM.topoutfolder)

    # process the data with the given parameters
    VM.nc_to_set_of_npy()    
    
