import bpy
import os

baseFolder=r"A:\anim_test"

#delete old watermesh
name = 'watersmooth'
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects[name].select_set(True)
bpy.ops.object.delete(confirm=False)


mat = bpy.data.materials['water']


def load_and_render_stl(filename, baseFolder=baseFolder, mat=mat, outfolder=r"A:\anim_test_png"):
	name = filename[:-4]
	
	bpy.ops.import_mesh.stl(filepath=os.path.join(baseFolder, filename))
	bpy.data.objects[name].data.materials.append(mat)
	
	outfile = os.path.join(outfolder, ''.join([name,'.png']))
	bpy.context.scene.render.filepath = outfile
	bpy.ops.render.render(write_still=True)
	
	#clean up
	bpy.ops.object.select_all(action='DESELECT')
	bpy.data.objects[name].select_set(True)
	bpy.ops.object.delete(confirm=False)
	
filenames = os.listdir(baseFolder)

for filename in filenames:
	if filename[-3:]==s'stl':
		load_and_render_stl(filename)
	