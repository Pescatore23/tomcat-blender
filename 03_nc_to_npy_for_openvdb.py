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
from time import sleep

# TODO: make this more elegant
try:
    import cupy as cp
    import cucim.skimage
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
    

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def find_free_GPU_memory(gpu_id, limit=0.5):
    free = cp.cuda.Device(gpu_id).mem_info[0]/cp.cuda.Device(gpu_id).mem_info[1]
    
    while free<limit:
        gpu_id = (gpu_id+1)%num_GPU #for all available GPUs
        sleep(2)
        free = cp.cuda.Device(gpu_id).mem_info[0]/cp.cuda.Device(gpu_id).mem_info[1]
        
    return gpu_id
        
    
    
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
        self.mask = args.mask
        self.mask_name = args.mask_name
        self.mask_dilate = args.mask_dilate
        self.erode = args.erode
    	
        
    def clean_binary_image(self, im, clean = True, remove_small=True,  minsize = 20, fp_radius = 1, i=0, GPU = True, GPU_avail=GPU_avail):
        if clean or remove_small:
            if GPU and GPU_avail:
                gpu_id = i%5 #num_GPU #use gpus 1 through 4, leaving the big A40 (0) alone or i%5 to use all 5
                gpu_id = find_free_GPU_memory(gpu_id)
                with cp.cuda.Device(gpu_id):
                    im = cp.array(im)
                    if clean: im = cucim.skimage.morphology.binary_opening(im, footprint=cucim.skimage.morphology.ball(fp_radius))
                    if remove_small: im = cucim.skimage.morphology.remove_small_objects(im, min_size=minsize)
                    if self.erode >0: im = cucim.skimage.morphology.binary_erosion(im, footprint=cucim.skimage.morphology.ball(self.erode))
                    im = cp.asnumpy(im)
                    mempool = cp.get_default_memory_pool()
                    mempool.free_all_blocks()
                
            else: 
                if clean: im = ndimage.binary_opening(im, structure=ball(fp_radius))
                if remove_small: im = morphology.remove_small_objects(im, min_size=minsize)
                if self.erode >0: im = ndimage.binary_erosion(im, structure=ball(self.erode))
            
        return im
    
    def xarray_to_npy(self, imdata, ts, i=0, GPU = True, GPU_avail=GPU_avail, overwrite=False):
        
        outpath = os.path.join(self.topoutfolder, self.array_name+'_phase_'+str(self.ph)+'_ts_'+f'{ts:04d}'+'.npy')
        
        if not os.path.exists(outpath) and not overwrite:
            # im = im.data
            im = imdata.sel(timestep=ts).data
            
            if self.mask:
                #  TODO: check if mask is int-binary 0-1 and adjust if necessary
                a,b,c,d,e,f = self.data.attrs['cropping of seg data']
                im = im[a:b,c:d,e:f]
                mask = self.data[self.mask_name].sel(timestep = ts).data
                
                if GPU and GPU_avail:
                    gpu_id = i%5 #num_GPU #use gpus 1 through 4, leaving the big A40 (0) alone or i%5 to use all 5
                    
                    gpu_id = find_free_GPU_memory(gpu_id)
                    with cp.cuda.Device(gpu_id):
                        mask = cp.array(mask)
                        mask = cucim.skimage.morphology.binary_dilation(mask, footprint=cucim.skimage.morphology.ball(self.mask_dilate))
                        mask = cp.asnumpy(mask)
                        mempool = cp.get_default_memory_pool()
                        mempool.free_all_blocks()
                    
                else: 
                    mask = ndimage.binary_dilation(mask, structure=ball(self.mask_dilate))
                
                # manual shift because membrane =0
                im = im -1
                
                im = im*mask
                
                # reshift
                im = im+1
            
            if not self.ph<0:
                im = im == self.ph
                im = self.clean_binary_image(im, i=i, clean = self.clean , remove_small=self.remove_small,  minsize = self.minsize, fp_radius = self.footprint)
        

        
        
            np.save(outpath, im)
        
    def nc_to_set_of_npy(self):
        imdata = self.data[self.array_name]
        
        if not self.mask:
            print('no mask considered')
        else:
            if self.mask_name in self.data.keys():
                print('use "'+self.mask_name+'" as mask')
            else:
                print('"'+self.mask_name+'" not found in dataset. no mask considered')
                self.mask = False
        
        if self.ts<0:
            print('processing all time steps')
            timesteps = imdata.timestep.data
            length = len(timesteps)
             
            Parallel(n_jobs=n_jobs, temp_folder=temp_folder)(delayed(self.xarray_to_npy)(imdata, timesteps[i], i) for i in range(length))
            # .sel(timestep=timesteps[i]).data
        else:
            print('processing time step ',str(self.ts))
            self.xarray_to_npy(imdata, self.ts)

if __name__ == '__main__':
    ### Parse arguments
    parser = argparse.ArgumentParser(description='preprocessing parameters')
    parser.add_argument('-o', '--output_path', type = str, default = '', help = 'path to folder that will contain the .npy files')
    parser.add_argument('-i', '--input_path', type=str, default='', help = 'path to the .nc-file containing the segmented data')
    parser.add_argument('-cl', '--clean_image', type = str2bool, default = True, help = 'wheter to remove spurious pixel by binaray opening')
    parser.add_argument('-fp', '--footprint', type = float, default = 1, help = 'radius of the sphere stencel used for the binary opening')
    parser.add_argument('-rs', '--remove_small', type = str2bool, default=True, help = 'wheter to remove objects smaller than minsize')
    parser.add_argument('-ms', '--minsize', type = int, default=20, help = 'minimum size of connected objects to keep')
    parser.add_argument('-ts', '--time_step', type = int, default=0, help = 'time step that is processed, -1 for all')
    parser.add_argument('-sn', '--segmented_name', type = str, default = 'segmented', help = 'name of the data array in the .nc')
    parser.add_argument('-ph', '--phase', type = int, default = 1, help='which phase to extract, -1 for all')
    parser.add_argument('-mk', '--mask', type = str2bool, default = False, help='wheter to use the mask in the segmented data (if available)')
    parser.add_argument('-mn', '--mask_name', type = str, default = '', help='name of the mask in the segmented data (if available)')
    parser.add_argument('-md', '--mask_dilate', type = int, default = 8, help='dilation radius of mask')
    parser.add_argument('-er', '--erode', type = int, default = 0, help='erosion radius')
    
    
    args = parser.parse_args()
    
    VM = volume_maker(args)
    
    # lazy load the data
    VM.data = xr.open_dataset(args.input_path)
    
    #create outfolder if necessary
    if not os.path.exists(VM.topoutfolder):
        os.mkdir(VM.topoutfolder)

    # process the data with the given parameters
    VM.nc_to_set_of_npy()    
    
