from pathlib import Path
import threading
import psutil
import time
import os
import logging
import csv
import pickle

import click
import graph_tool.all as gt
import polars as pl
import numpy as np

logging.basicConfig(level=logging.DEBUG, format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")

def analyse(output_dir: Path):
    graph_ncol = output_dir / 'graph.ncol'
    states_dir = output_dir / 'block_states'
    block_state_path = states_dir / 'over_otimized.pkl'

    def edges(tmp_file):
        with open(tmp_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                yield tuple(row)

    logging.info("Loading graph...")
    g = gt.Graph(edges(graph_ncol), hashed=True, directed=False)

    logging.info("Loading block state...")
    with open(block_state_path, "rb") as f:
        bs = pickle.load(f)

    bs[0] = g.own_property(bs[0])
    state = gt.NestedBlockState(g, bs=bs)

    logging.info("Equilibrating Markov chain...")
    gt.mcmc_equilibrate(state, wait=100, mcmc_args=dict(niter=10))

    samples = [] # collect some partitions
    def collect_partitions(s):
        nonlocal samples
        samples.append(s.get_bs())

    # Now we collect partitions for exactly 10,000 sweeps, at intervals
    # of 10 sweeps:
    logging.info("Collecting partitions...")
    gt.mcmc_equilibrate(state, force_niter=1000, mcmc_args=dict(niter=10),
                        callback=collect_partitions)

    logging.info("Saving partitions...")
    with open(output_dir / "posterior_samples.pkl", "wb") as f:
        pickle.dump(bs, f)

@click.command()
@click.argument("output_dir", type=click.Path(exists=True))
def main(output_dir):
    analyse(Path(output_dir))

if __name__ == "__main__":
    main()
