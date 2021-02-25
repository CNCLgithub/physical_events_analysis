#!/usr/bin/env bash

#SBATCH --output=calculate-%j.out
#SBATCH -p short
#SBATCH -t 4:00:00
#SBATCH --mem 5G

#I think all I really need is to load fmriprep
module load Python/miniconda

source activate /gpfs/milgram/project/turk-browne/users/tsy6/conda_envs/video

vid_num=$1

python pixel_change_calculations.py $vid_num