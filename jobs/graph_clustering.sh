#!/bin/bash
#SBATCH --job-name=graph_clu
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=32GB
#SBATCH --cpus-per-task=8
#SBATCH --time=100:00:00
#SBATCH --output=out/graph_clu%j.out
#SBATCH --error=err/graph_clu%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/home/lleal/programs/plasmidEvo/rslts"
SCRIPTSDIR="scripts/"

pixi run python "${SCRIPTSDIR}/graph_clustering.py" "${WORKDIR}"
