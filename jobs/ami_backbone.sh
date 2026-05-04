#!/bin/bash
#SBATCH --job-name=backbone
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=40GB
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00
#SBATCH --output=out/backbone%j.out
#SBATCH --error=err/backbone%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/scratch/local/lleal/plasmid_evo"
SCRIPTSDIR="scripts/"

pixi run python "${SCRIPTSDIR}/ami_backbone.py"

