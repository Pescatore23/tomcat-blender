import bpy
import os

baseFolder="/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/3II/crack/" #for stl
outfolder="/mpc/homes/fische_r/NAS/DASCOELY/processing/04_membrane_ML/3II/crack_cathode_camera_png/" #for png

material = 'crack' #'Crack'


if not os.path.exists(outfolder):
    os.mkdir(outfolder)

# print('Warning: this is a crude hack. Make sure the names are capturing the correct objects')

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
	
