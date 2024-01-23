import bpy
import pyopenvdb as openvdb
import numpy as np

Volume = np.load('/mpc/homes/fische_r/NAS/DASCOELY/processing/02_registered_3p1D/3II_ts_4_registered.npy')
Volume = Volume/25000
Volume = Volume[20:-20,20:-20,200:-500]

grid = openvdb.FloatGrid()

grid.copyFromArray(Volume.astype(float))


#grid.transform = openvdb.createLinearTransform([[1, 0, 0, 0,], [0, 1, 0, 0], [0,0,1,0],[0,0,0,1]])

grid.gridClass = openvdb.GridClass.FOG_VOLUME
grid.name = 'density'

openvdb.write('/mpc/homes/fische_r/NAS/DASCOELY/processing/02_registered_3p1D/3II_ts_4_registered.vdb', grid)

bpy.ops.object.volume_import(filepath = '/mpc/homes/fische_r/NAS/DASCOELY/processing/02_registered_3p1D/3II_ts_4_registered.vdb', files=[])