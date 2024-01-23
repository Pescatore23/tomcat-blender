# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 14:53:48 2023

converts numpy array to openvdb

run within blender to use pyopenvdb, it would eventually be nice to use pyopenvdb outside blender to have the conversion in one go

@author: fische_r
"""

import os
import numpy as np
import pyopenvdb as openvdb


sample = '3II'
ts = 28

inpath = os.path.join('/mpc/homes/fische_r/NAS/DASCOELY/processing/06_anode_CL', sample, str(ts)+'_cropped_to_membrane_ML.npy')
outpath = os.path.join('/mpc/homes/fische_r/NAS/DASCOELY/processing/06_anode_CL', sample, str(ts)+'_cropped_to_membrane_ML.vdb')
#modified crops, comment out
x1 = 20
x2 = -20
y1 = 0
y2 = -1
z1 = 20
z2 = -20

def convert_npy_to_vdb(inpath, outpath, x1, x2, y1,y2, z1, z2):
    im = np.load(inpath)
    im = im[x1:x2,y1:y2,z1:z2]

    
    grid = openvdb.FloatGrid()
    grid.copyFromArray(im.astype(float))
    grid.gridClass = openvdb.GridClass.FOG_VOLUME
    grid.name = 'density'
    
    openvdb.write(outpath, grid)
    


convert_npy_to_vdb(inpath, outpath, x1, x2, y1,y2, z1, z2)


