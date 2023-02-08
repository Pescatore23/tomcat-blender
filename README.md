# tomcat_blender

![lstopo](img/tomcat_blender_logo_sketch.png)

Scripts to automate TOMCAT data visualization in blender with python.
TODO:
- [ ] make cool logo from current sketch
- [ ] build into python module with classes
- [ ] maybe wrap system call of blender
- [x] add cupy/cucim support (partly done)
- [ ] use openvdb for volume import in blender

required packages: xarray, scikit-image, trimesh, numpy

## How to use

1. Extract series stl-files for desired time series with e.g. 01_extract_surfaces.py

1. Choose appropitate time step to set up scene and everything (e.g. cycles-render) in blender, do a test render, save the blend-file

1. Run the animation script from command line

	Windows

	```bash
	<path_to_binary>blender.exe blend-file.blend --background --python testanimscriptfull.py
	```
1. (optional) adjust frame and sampling rate, better option: create separate avi-files, merge and convert to mkv, e.g. combining ImageJ and ffmpeg
