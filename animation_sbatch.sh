#!/bin/bash -l
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=200GB
#SBATCH -p gpu-long
#SBATCH --gres=gpu:2

blenderrun $1 -a --background