import bpy
import os

baseFolder="/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/3II/membrane_smaller_200_removed/" #for stl
baseFolder2 = "/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/3II/crack_smaller_200_removed/" 
outfolder="/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/3II/membrane_crack_anode_camera_png/" #for png

material = 'membrane' #'Crack'
material2 =  'Crack'

if not os.path.exists(outfolder):
    os.mkdir(outfolder)

# print('Warning: this is a crude hack. Make sure the names are capturing the correct objects')

#delete old reference object
name = 'reference'
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects[name].select_set(True)
bpy.ops.object.delete(confirm=False)


mat = bpy.data.materials[material]
mat2 = bpy.data.materials[material2]

def load_and_render_stl(filename, filename2, baseFolder=baseFolder, mat=mat, outfolder=outfolder):
	name = filename[:-4]
	name2 = filename2[:-4]

	bpy.ops.import_mesh.stl(filepath=os.path.join(baseFolder, filename), axis_up='-Z')
	bpy.data.objects[name].data.materials.append(mat)

	bpy.ops.import_mesh.stl(filepath=os.path.join(baseFolder2, filename2), axis_up='-Z')
	bpy.data.objects[name2].data.materials.append(mat2)
	
	outfile = os.path.join(outfolder, ''.join([name,'.png']))
	bpy.context.scene.render.filepath = outfile
	bpy.ops.render.render(write_still=True)
	
	#clean up
	bpy.ops.object.select_all(action='DESELECT')
	bpy.data.objects[name].select_set(True)
	bpy.ops.object.delete(confirm=False)
	
filenames = os.listdir(baseFolder)
filenames2 = os.listdir(baseFolder2)

filenames.sort()
filenames2.sort()

for (filename, filename2) in zip(filenames,filenames2):
	if filename[-3:]=='stl':
		load_and_render_stl(filename, filename2)
	
