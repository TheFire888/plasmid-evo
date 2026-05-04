import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import taxopy as tx
import pickle
import csv
import graph_tool.all as gt
import logging
logging.basicConfig(
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        )

from sklearn.metrics import adjusted_mutual_info_score
from pathlib import Path
from tqdm import tqdm

taxdb = tx.TaxDb()

project_root = Path("/home/lleal/programs/plasmidEvo/")
data_dir = project_root / 'data'
output_dir = project_root / 'rslts'

plasmid_metrics = output_dir / 'plasmid_metrics.tsv'
block_state_path = output_dir / 'block_states' / 'over_otimized.pkl'
tree_file = output_dir / 'over_otimized_cluster_paths_02.tsv'
protein_cluster_file = output_dir / 'protein_clusters.tsv'
annotation_path = output_dir / 'annotations' / 'annotations.tsv'
metadata_path = project_root / 'data' / 'sequence_metadata.tsv'
conj_path = output_dir / 'conjscan.tsv'
mob_path = output_dir / 'plasmids_simple_mob_typer.tsv'
graph_path = output_dir / 'graph.ncol'
ami_path = output_dir / 'ami.tsv'

tree_df = pl.scan_csv(tree_file, separator='\t', has_header=False, new_columns=[
    'id', 'name', 'h0', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9'
]).with_columns(pl.col("name").str.strip_chars("'"))

plasmids_df = (
    tree_df
    .filter(~pl.col("name").str.contains(r"_\d+$"))
    .select(["id", "name"] + [f"h{i}" for i in range(9)])
).join(pl.scan_csv(plasmid_metrics, separator='\t'), left_on="name", right_on="#id")


gene_clusters = pl.scan_csv(
    protein_cluster_file,
    separator="\t",
    has_header=False,
    new_columns=["cluster_rep", "gene"]
).with_columns(
    pl.col("gene").str.replace(r"_\d+$", "").alias("plasmid")
)

presence = (
    gene_clusters
    .group_by(["cluster_rep", "plasmid"])
    .agg(pl.len().alias("count"))
    .with_columns(pl.lit(1).alias("present"))
    .select(["cluster_rep", "plasmid", "present"])
)

df = presence.join(
    plasmids_df,
    left_on="plasmid",
    right_on="name",
    how="inner"
).collect(engine='streaming')

ls = []
lvl = 'h0'

for i, unique_gene in tqdm(enumerate(df['cluster_rep'].unique())):
    logging.info(f"{i}: calculating AMI for {unique_gene}")
    gene_mask = (df['cluster_rep'] == unique_gene).to_numpy()

    for j, cid in tqdm(enumerate(df[lvl].unique())):
        cluster_mask = (df[lvl] == cid).to_numpy()

        ami = adjusted_mutual_info_score(gene_mask, cluster_mask)
        ls.append((unique_gene, cid, ami))

ami_df = pl.DataFrame(ls, orient="row")

ami_df.write_csv(ami_path, separator='\t')
