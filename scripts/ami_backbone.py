import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
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

lvl = 'h7'
ami_path = output_dir / f'{lvl}_ami.tsv'

df = presence.join(
    plasmids_df,
    left_on="plasmid",
    right_on="name",
    how="inner"
).group_by(pl.col('plasmid')).agg(
    pl.col('cluster_rep'), pl.col(lvl).mode().first()
).sort('plasmid').collect(engine='streaming')

gene_in_cid = (
    df.explode('cluster_rep')
    .group_by(lvl)
    .agg(pl.col('cluster_rep').unique())
    .to_dict(as_series=False)
)

cid_to_genes = {
    cid: set(genes)
    for cid, genes in zip(gene_in_cid[lvl], gene_in_cid['cluster_rep'])
}

genes = df.explode('cluster_rep').get_column('cluster_rep').unique()
print(len(genes))
cids = df[lvl].unique()

gene_in_cid = df.group_by(pl.col(lvl)).agg(pl.col('cluster_rep'))

# genes_done = pl.read_csv(first_ami_path, separator='\t', has_header=False, new_columns=['cluster_rep', 'h0', 'ami']).select(['cluster_rep']).rows()

with ami_path.open(mode='wb', buffering=0) as f_out:
    for i, unique_gene in enumerate(genes):
        # if unique_gene in genes_done: continue
        logging.info(f"{i} {unique_gene}")
        gene_mask = (df['cluster_rep'].list.contains(unique_gene))

        for j, cid in enumerate(cids):
            if unique_gene not in cid_to_genes[cid]:
                continue

            cluster_mask = (df[lvl] == cid)

            ami = adjusted_mutual_info_score(gene_mask, cluster_mask)
            if ami > 0.5:
                f_out.write(f'{unique_gene}\t{cid}\t{ami}\n'.encode("utf-8"))
                logging.info(f"Significant ami for {unique_gene} in {cid}!")
