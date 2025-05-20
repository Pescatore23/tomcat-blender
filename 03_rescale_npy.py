# python
import numpy as np
import os
import skimage.transform
from joblib import Parallel,delayed

npypath = '/home/esrf/rofische/data_ihma664/NOBACKUP/wood/wood/blender_data/npy'

files = os.listdir(npypath)

def file_function(file):
	if not file in ['segmented_phase_-1_ts_0086.npy', 'segmented_phase_-1_ts_0001.npy']:
		im = np.load(os.path.join(npypath, file))
		im = skimage.transform.rescale(im, 0.5, preserve_range=True, anti_aliasing=True).astype(np.uint8)
		np.save(os.path.join(npypath, file), im)

Parallel(n_jobs=16, temp_folder='/tmp/robert')(delayed(file_function)(file) for file in files)
