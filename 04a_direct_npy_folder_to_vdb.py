import argparse
import os
import numpy as np
import openvdb

parser = argparse.ArgumentParser(description='preprocessing parameters')
parser.add_argument('-i', '--input_path', type=str, default='', help = 'folder containing the npy')
parser.add_argument('-o', '--output_path', type = str, default = '', help = 'path to folder that will contain the .vdb files')
parser.add_argument('-cr', '--crop_image', type=str, default = '0,-1,0,-1,0,-1', help = 'cropping indices')

args = parser.parse_args()

path = args.input_path
vdbpath = args.output_path
crops = args.crop_image
print(crops)

crops = [int(item) for item in crops.split(",")]

a,b,c,d,e,f = crops

if not os.path.exists(vdbpath):
    os.mkdir(vdbpath)

for file in os.listdir(path):
    if file[-3:] == 'npy':
        print(file)
        vdbfile = file.replace('npy', 'vdb')
        im = np.load(os.path.join(path, file))

        im = im[a:b,c:d,e:f]

        grid = openvdb.FloatGrid()
        grid.copyFromArray(im.astype(float))
        grid.gridClass = openvdb.GridClass.FOG_VOLUME
        grid.gridClass = openvdb.GridClass.FOG_VOLUME
        grid.name = 'density'
        openvdb.write(os.path.join(vdbpath,vdbfile), grid)

        
        
