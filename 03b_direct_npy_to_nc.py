import numpy as np
import argparse
import openvdb

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type = str, default = '', help = ".npy")

path = args.path
vdbpath = pat.replace('npy', 'vdb'

im = np.load(path)

grid = openvdb.FloatGrid()

grid.copyFromArray(im.astype(float))
grid.gridClass = openvdb.GridClass.FOG_VOLUME
grid.gridClass = openvdb.GridClass.FOG_VOLUME
grid.name = 'density'
openvdb.write(vdbpath, grid)