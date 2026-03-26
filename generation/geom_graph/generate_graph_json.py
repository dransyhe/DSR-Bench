"""
Generate JSON ground-truth graph files for geom_graph GED evaluation.

For each construct_{k}d/construct_{mode}.txt, reads Nodes + Threshold,
rebuilds the graph, and writes construct_{k}d/construct_{mode}_graph.json
as a list of {"nodes": [...], "edges": [...]} dicts.

Usage (from repo root):
    python -m generation.geom_graph.generate_graph_json
"""
import ast
import json
import os
import numpy as np
import networkx as nx
from scipy.spatial import cKDTree


def build_graph(nodes, threshold):
    pts = np.asarray(nodes, dtype=float)
    tree = cKDTree(pts)
    neighbours = tree.query_ball_tree(tree, r=threshold)
    G = nx.Graph()
    G.add_nodes_from(map(tuple, pts))
    for i, nbrs in enumerate(neighbours):
        for j in (j for j in nbrs if j > i):
            u, v = tuple(pts[i]), tuple(pts[j])
            dist = float(np.linalg.norm(pts[i] - pts[j]))
            G.add_edge(u, v, weight=dist)
    return G


def graph_to_dict(G):
    return {
        "nodes": [list(n) for n in G.nodes()],
        "edges": [[list(u), list(v)] for u, v in G.edges()],
    }


if __name__ == "__main__":
    for k in [1, 2, 3, 5]:
        for mode in ["easy", "medium", "hard"]:
            input_path = f"generation/geom_graph/construct_{k}d/construct_{mode}.txt"
            output_path = f"generation/geom_graph/construct_{k}d/construct_{mode}_graph.json"
            if not os.path.exists(input_path):
                continue
            graphs = []
            nodes, threshold = None, None
            with open(input_path) as f:
                for line in f:
                    if line.startswith("Nodes:"):
                        nodes = ast.literal_eval(line.split(":", 1)[1].strip())
                    elif line.startswith("Threshold:"):
                        threshold = float(line.split(":", 1)[1].strip())
                    elif line.startswith("BFS:"):
                        G = build_graph(nodes, threshold)
                        graphs.append(graph_to_dict(G))
            with open(output_path, "w") as f:
                json.dump(graphs, f)
            print(f"Wrote {len(graphs)} graphs to {output_path}")
