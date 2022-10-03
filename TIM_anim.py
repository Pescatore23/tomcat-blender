import bpy
import os

baseFolder=r"A:\anim_test_full" #for stl
outfolder=r"A:\anim_test_full_png2" #for png

baseFolder = '/mpc/homes/fische_r/NAS/testing/TIM_tomo/cropped/stl/water'
outfolder =  '/mpc/homes/fische_r/NAS/testing/TIM_tomo/cropped/water_anim'

if not os.path.exists(outfolder):
    os.mkdir(outfolder)

# print('Warning: this is a crude hack. Make sure the names are capturing the correct objects')

#delete old watermesh
name = 'watersmooth'
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects[name].select_set(True)
bpy.ops.object.delete(confirm=False)


mat = bpy.data.materials['water']

def load_and_render_stl(filename, baseFolder=baseFolder, mat=mat, outfolder=outfolder):
	name = filename[:-4]
	
	bpy.ops.import_mesh.stl(filepath=os.path.join(baseFolder, filename), axis_up='-Y')
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
	if filename[-3:]=='stl':
		load_and_render_stl(filename)
	