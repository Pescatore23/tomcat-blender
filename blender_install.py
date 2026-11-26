# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 10:28:34 2026

@author: ROFISCHE
"""

import argparse
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--module', type = str, default = '', help = "name of the pip module to install")

args = parser.parse_args()
module = args.module

subprocess.check_call([sys.executable, "-m", "pip", "install", module])