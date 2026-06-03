import argparse
import os
import numpy as np
import openvdb

parser = argparse.ArgumentParser(description='preprocessing parameters')
parser.add_argument('-i', '--input_path', type=str, default='', help = 'folder containing the npy')
parser.add_argument('-o', '--output_path', type = str, default = '', help = 'path to folder that will contain the .vdb files')

args = parser.parse_args()

path = args.input_path
vdbpath = args.output_path

if not os.path.exists(vdbpath):
    os.mkdir(vdbpath)

for file in os.listdir(path):
    if file[-3:] == 'npy':
        print(file)
        vdbfile = file.replace('npy', 'vdb')
        im = np.load(os.path.join(path, file))

        grid = openvdb.FloatGrid()
        grid.copyFromArray(im.astype(float))
        grid.gridClass = openvdb.GridClass.FOG_VOLUME
        grid.gridClass = openvdb.GridClass.FOG_VOLUME
        grid.name = 'density'
        openvdb.write(os.path.join(vdbpath,vdbfile), grid)

        
        
