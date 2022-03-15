import bpy
bpy.context.scene.render.filepath = r"Z:\users\firo\blender\test\test_water3.png"
bpy.ops.render.render(write_still=True)

print('Warning: this is a crude hack. Make sure the names are capturing the correct objects')

#delete old watermesh
name = 'watersmooth'
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects[name].select_set(True)
bpy.ops.object.delete(confirm=False)


#import new mesh
name = 'watertest'
bpy.ops.import_mesh.stl(filepath=r"A:\watertest.stl")

mat = bpy.data.materials['water']
bpy.data.objects[name].data.materials.append(mat)

bpy.context.scene.render.filepath = r"Z:\users\firo\blender\test\test_water_not_smooth.png"
bpy.ops.render.render(write_still=True)