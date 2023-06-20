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


toppath = '/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/3II/crack_npy'
topoutpath = '/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/3II/crack_vdb'


x1, x2 = (0,-1)
y1, y2  = (0,-1)
z1, z2 = (0,-1)
ts = -1
# ts = 40

#modified crops, comment out
x1, x2 = (10,-10)
y1, y1  = (10,-10)
z1, z2 = (10,-10)

def check_npy_folder(toppath):
    files = []
    for file in os.listdir(toppath):
        if file[-3:] == 'npy':
            files.append(file)
    return files

def convert_npy_to_vdb(file, toppath, topoutpath, x1,x2,y1,y2,z1,z2):
    im = np.load(os.path.join(toppath,file))
    im = im[x1:x2,y1:y2,z1:z2]
    im = im*1.0
    
    grid = openvdb.FloatGrid()
    grid.copyFromArray(im.astype(float))
    grid.gridClass = openvdb.GridClass.STAGGERED
    grid.name = 'density'
    
    openvdb.write(os.path.join(topoutpath, file[:-3]+'vdb'), grid)
    


files = check_npy_folder(toppath)
files.sort()

if ts <0:
    for i in range(len(files)):
        convert_npy_to_vdb(files[i], toppath, topoutpath, x1, x2, y1, y2, z1, z2)
else:
    file = files[ts]
    print(file)
    convert_npy_to_vdb(file, toppath, topoutpath, x1,x2,y1,y2,z1,z2)


