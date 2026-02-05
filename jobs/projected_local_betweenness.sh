#!/bin/bash
#SBATCH --job-name=local_bet
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=86GB
#SBATCH --cpus-per-task=4
#SBATCH --time=100:00:00
#SBATCH --output=out/local_bet%j.out
#SBATCH --error=err/local_bet%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

pixi run python scripts/projected_local_betweenness.py
