import graph_tool.all as gt
import polars as pl
from tqdm import tqdm

from pathlib import Path
import csv

project_root = Path("/home/lleal/programs/plasmidEvo/")
output_dir = project_root / 'rslts'
graph_path = output_dir / 'graph.ncol'

def edges(path):
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            yield tuple(row)

g = gt.Graph(edges(graph_path), hashed=True, directed=False)

def is_plasmid(g, vertex):
    return '_' not in g.vp['ids'][vertex]

proj = g.new_vp('bool', vals=[is_plasmid(g, v) for v in g.vertices()])

pg, props = gt.graph_projection(g, proj, props=[g.vertex_index, g.vp.ids])

def get_local_betweenness(g, props, neighbourhood_size=3):
    local_betweenness = []
    node_ids = [] # Armazena os IDs para o DataFrame

    def get_k_order_neighbours(g, start_vertex, K):
        visited = {start_vertex}
        current_level_nodes = {start_vertex}
        all_neighbors = [int(start_vertex)]

        for current_k in range(K):
            next_level_nodes = set()
            for node in current_level_nodes:
                for neighbor in node.out_neighbors():
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_level_nodes.add(neighbor)
                        all_neighbors.append(int(neighbor))
            current_level_nodes = next_level_nodes
        return all_neighbors

    for node in tqdm(g.vertices()):
        k_order_neighbours = get_k_order_neighbours(g, node, neighbourhood_size)
        k_order_filter = g.new_vertex_property('bool')
        for neighbour in k_order_neighbours:
            k_order_filter[neighbour] = True

        subgraph = gt.GraphView(g, vfilt=k_order_filter)
        vb, _ = gt.betweenness(subgraph)

        print(f"{props[0][node]}\t{props[1][node]}\t{vb[node]}")

get_local_betweenness(pg, props)

