#!/bin/bash
#SBATCH --job-name=infomap
#SBATCH --partition=max50
#SBATCH --ntasks=1
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=4
#SBATCH --time=100:00:00
#SBATCH --output=out/infomap%j.out
#SBATCH --error=err/infomap%j.err

export PATH="/home/lleal/.pixi/bin:$PATH"

echo -e "\n## Job ${SLURM_JOB_ID} iniciado em $(date +'%d-%m-%Y as %T') ##\n"

WORKDIR="/home/lleal/programs/rust_pajek"

pixi run infomap \
    "${WORKDIR}/semi-bipartite.net" \
    "${WORKDIR}" \
    --seed 888 \
    --num-trials 1 \
    --flow-model "undirected" \
    --two-level \
    --ftree \
    -vvv
