# Image processing in python

This page contains links to python tools primarly for image processing available at Empa's gitlab.

## ROBert's PYthon LIBrary (robpylib)

A collection of often used routines. Useful for image IO.

Requires git and pre-installation of python modules via `conda` recommended. Can be installed by:

```
pip install git+https://gitlab.empa.ch/firo/robpylib.git
```
	
## TOMCAT processing

Methods (mostly python) employed to process and post-process large time-resolved X-ray tomographic microscopy datasets on wicking in yarns. Contains for example, parallelized image registration, machine-learning segmentation or surface mesh extraction. Requires robpylib and Fiji/ImageJ with the xlib and Trainable Weka segmentation plugins.

```
git clone https://gitlab.empa.ch/firo/tomcat-processing.git
```
	
I will attempt to improve the description and documentation in the future.

## ICON processing

Methods (mostly python) employed to process and post-process neutron radiography on uptake in textiles. The code is pretty messy and inefficient. Recommended to take interesting methods, but re-develop if necessary.

```
git clone https://gitlab.empa.ch/firo/icon-processing.git
```

## VIS processing

Methods to process and post-process time series of backlight photography taken with Nikon D90 on wicking in thin electro-spun membranes.

```
git clone https://gitlab.empa.ch/firo/espun-membrane-processing.git	
```
	
## Volume visualization in Blender with python

This is a repository to automatically render beautifully 4D-image data. In development, keep posted!

```
git clone https://gitlab.empa.ch/firo/tomcat_blender.git	
```

## Videos

Convert ImageJ-avi to mkv as recommended by the ETH research collection for long time storage. 

```
ffmpeg -i input.avi output.mkv -acodec libfaac -vcodec ffv1
```

currently best working method to get videos suitable for ppt-presentations:

```
ffmpeg -i input-video.mkv -vf "crop=trunc(iw/2)*2:trunc(ih/2)*2" -q:a 2 -q:v 4 -vcodec wmv2 -acodec wmav2 output-video.avi
```

