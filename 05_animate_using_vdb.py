# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 15:47:22 2023

@author: fische_r
"""

import bpy
import os

baseFolder="/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/3II/crack_vdb/" #for vdb
outfolder="/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/3II/crack_cathode_camera_png_test/" #for png

material = 'crack' #'Crack'


if not os.path.exists(outfolder):
    os.mkdir(outfolder)
    
#delete old reference object
name = 'reference'
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects[name].select_set(True)
bpy.ops.object.delete(confirm=False)

mat = bpy.data.materials[material]

def load_and_render_stl(filename, baseFolder=baseFolder, mat=mat, outfolder=outfolder):
    name = filename[:-4]
    outfile = os.path.join(outfolder, ''.join([name,'.png']))
    if not os.path.exists(outfile):

        bpy.ops.import_mesh.stl(filepath=os.path.join(baseFolder, filename), axis_up='-Z')
        
        bpy.ops.object.volume_import(filepath="/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/3II/crack_vdb/"+name+".vdb",
                                     directory="/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/3II/crack_vdb/",
                                     files=[],
                                     align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

        
        bpy.data.objects[name].data.materials.append(mat)
        bpy.context.scene.render.filepath = outfile
        bpy.ops.render.render(write_still=True)

        #clean up
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[name].select_set(True)
        bpy.ops.object.delete(confirm=False)
	
filenames = os.listdir(baseFolder)

for filename in filenames:
	if filename[-3:]=='stl':
		load_and_render_stl(filename)