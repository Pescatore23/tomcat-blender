 # -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 14:53:48 2023

converts numpy array to openvdb

run within blender to use pyopenvdb, it would eventually be nice to use pyopenvdb outside blender to have the conversion in one go

@author: fische_r
"""

import os
import numpy as np
import openvdb


toppath = '/home/esrf/rofische/data_ihma664/PROCESSED_DATA/TOMCAT/Tomcat_2/R_m4_33_050_2/blender_data/npy/'
#toppath2 = '/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/5II/crack_npy'
topoutpath = '/home/esrf/rofische/data_ihma664/PROCESSED_DATA/TOMCAT/Tomcat_2/R_m4_33_050_2/blender_data/vdb'

if not os.path.exists(topoutpath):
    os.mkdir(topoutpath)
    
overwrite = False


x1 = 0
x2 = -1
y1 = 0
y2 = -1
z1 = 0
z2 = -1
ts = -1
#ts = 0

#modified crops, comment out
#x1 = 20
#x2 = -20
#y1 = 20
#y2 = -20
#z1 = 20
#z2 = -20

def check_npy_folder(toppath):
    files = []
    for file in os.listdir(toppath):
        if file[-3:] == 'npy':
            files.append(file)
    return files

def convert_npy_to_vdb(file,toppath, topoutpath, x1,x2,y1,y2,z1,z2):
    im = np.load(os.path.join(toppath,file))
    
    # special crop for sample 4 GDL
#    im[:,:170,:] = False
 #   im[:,:,:230] = False
    
    imc = im[x1:x2,y1:y2,z1:z2]
    imc[imc==3] = 1
    #imc[~(imc==2)] = 0 # line to only get water
    #imc[~(imc==1)] = 0 # line to only get solid
    #imc[imc==1] = 2 # line to convert binary water to color water
    # im1 = imc == 0
    # im2 = imc == 2
    
    # imc = im1*1.0 + im2*2.0
    imc = im*1.0
    
    grid = openvdb.FloatGrid()
    grid.copyFromArray(imc.astype(float))
    grid.gridClass = openvdb.GridClass.FOG_VOLUME
    grid.name = 'density'
    
    openvdb.write(os.path.join(topoutpath, file[:-3]+'vdb'), grid)
    


files = check_npy_folder(toppath)
files.sort()


if ts <0:
    for i in range(len(files)):
        file = files[i]
        if not os.path.exists(os.path.join(topoutpath, file[:-3]+'vdb')) and not overwrite:
            convert_npy_to_vdb(file,toppath, topoutpath, x1, x2, y1, y2, z1, z2)
else:
    file = files[ts]
    print(file)
    convert_npy_to_vdb(file,toppath,topoutpath, x1,x2,y1,y2,z1,z2)


