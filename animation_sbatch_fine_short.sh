#!/bin/bash -l
#SBATCH --time=2:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=200GB
#SBATCH -p gpu
#SBATCH --gres=gpu:2

/data/id19/inhouse/robert/blender-5.1.2-linux-x64/blender -b $1 -s $2 -e $3 -a --background
