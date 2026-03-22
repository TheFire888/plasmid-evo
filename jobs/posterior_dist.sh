#!/bin/bash
#SBATCH --job-name=posterior_dist
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=1
#SBATCH --time=190:00:00
#SBATCH --output=out/posterior_dist%j.out
#SBATCH --error=err/posterior_dist%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"
SCRIPTSDIR="scripts/"

pixi run python "${SCRIPTSDIR}/posterior_dist.py" "${WORKDIR}"
