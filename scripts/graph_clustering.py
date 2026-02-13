from pathlib import Path
import threading
import psutil
import time
import os
import logging
import csv

import click
import graph_tool.all as gt
import polars as pl

logging.basicConfig(level=logging.DEBUG, format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")

def log_memory():
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / 1024**2
        logging.debug(f"Monitor: {mem:.2f} MB em uso")
        time.sleep(60)

threading.Thread(target=log_memory, daemon=True).start()

def analyse(output_dir: Path):
    graph_ncol = output_dir / 'graph.ncol'
    states_dir = output_dir / 'block_states'

    def edges(tmp_file):
        with open(tmp_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                yield tuple(row)

    logging.info("Loading graph...")
    g = gt.Graph(edges(graph_ncol), hashed=True, directed=False)

    logging.info("Minimizing nested blockmodel...")
    state = gt.minimize_nested_blockmodel_dl(g)

    logging.info("Optimizing...")
    gt.mcmc_anneal(
        state,
        beta_range=(0.5, 30),
        niter=2000,
        mcmc_equilibrate_args=dict(force_niter=20)
    )

    block_state = state.get_bs()

    logging.info("Saving output...")
    with open(states_dir / 'otimized.pkl', 'wb') as fh:
        pickle.dump(block_state, fh)

    def save_paths(g, state):
        output_path = output_dir / 'otimized_cluster_paths_02.tsv'
        lvls = state.get_levels()
        avail = []

        with open(output_path, 'w') as f_out:
            for lvl in lvls:
                if lvl.get_N() == 1:
                    break
                avail.append(lvl)

            for i, node in enumerate(g.vp['ids']):
                path = [str(i), f"'{node}'"]
                
                r = lvls[0].get_blocks()[i]

                path.append(str(r))
                
                for j in range(1,len(avail)):
                    r = lvls[j].get_blocks()[r]
                    path.append(str(r))

                f_out.write(f"{'\t'.join(path)}\n")

    save_paths(g, state)


@click.command()
@click.argument("output_dir", type=click.Path(exists=True))
def main(output_dir):
    analyse(Path(output_dir))

if __name__ == "__main__":
    main()
