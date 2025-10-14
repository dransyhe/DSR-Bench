from __future__ import annotations
from typing import Sequence, Iterable
import numpy as np
from numpy import random
import networkx as nx
from scipy.spatial import cKDTree
from collections import deque
from utils import plot_geom_graph_2d

def generate_random_geom_graphs(data, threshold=20):
    """
    Generates Euclidean graphs with random nodes and edges.
    Edges weights are generated based on the Euclidean distance between nodes.
    """
     # --- normalise input ---------------------------------------------------
    pts = np.asarray(data, dtype=float)
    if pts.ndim != 2:
        raise ValueError("`data` must be a 2-D array-like: shape (n_points, k)")
    n, k = pts.shape
    if n == 0:
        raise ValueError("`data` must contain at least one point")
    
    tree = cKDTree(pts)
    neighbours: Iterable[list[int]] = tree.query_ball_tree(tree, r=threshold)

    G = nx.Graph()
    G.add_nodes_from(map(tuple, pts))
    
    for i, nbrs in enumerate(neighbours):
        for j in (j for j in nbrs if j > i):
            u, v = tuple(pts[i]), tuple(pts[j])
            dist = float(np.linalg.norm(pts[i] - pts[j], ord=2))
            G.add_edge(u, v, weight=dist)
    
    return G 

def weighted_bfs_edges(G, source, weight="weight"):
    """
    Iterate over edges in a breadth-first search of `G`, but always
    explore the lightest outgoing edges of each vertex first.

    Parameters
    ----------
    G : networkx.Graph or networkx.DiGraph
        The weighted graph.
    source : node
        Start vertex.
    weight : str
        Edge-attribute key storing the weight (default = "weight").

    Yields
    ------
    (u, v) : 2-tuple
        The tree edges of the BFS in the order they are traversed.
    """
    seen = {source}
    q = deque([source])

    while q:
        u = q.popleft()

        # Collect unseen neighbours with their edge weights
        nbrs = [
            (G[u][v].get(weight, 1), v)          # (w_uv, v)
            for v in G.neighbors(u)
            if v not in seen
        ]
        # Visit lightest edges first
        nbrs.sort(key=lambda x: x[0])

        for _, v in nbrs:
            seen.add(v)
            q.append(v)
            yield u, v


def weighted_bfs_tree(G, source, weight="weight"):
    """
    Return an ordered list of vertices in the order they are first
    discovered by `weighted_bfs_edges`.
    """
    order = [source]
    for _, v in weighted_bfs_edges(G, source, weight):
        order.append(v)
    return order


if __name__ == "__main__":
    
    k = 1
    threshold = 30
    for mode in ["easy", "medium", "hard"]:
        path = "generation/geom_graph"
        with open(f"generation/geom_graph/construct_{k}d/construct_{mode}.txt", "w") as f:
            if mode == "easy":
                min_n = 5
                max_n = 10
            elif mode == "medium":
                min_n = 11
                max_n = 20
            else:
                min_n = 21
                max_n = 30
            edge_prob = 0.3 

            for i in range(30):
                f.write(f"Graph {i}\n")
                n = random.randint(min_n, max_n)
                rng = np.random.default_rng(i)
                data = rng.uniform(0, 100, size=(n, k)).round(2)
                G = generate_random_geom_graphs(data, threshold=threshold)
                traverse = weighted_bfs_tree(G, list(G.nodes())[0], weight="weight")
                f.write("Nodes: " + str([list(dt) for dt in data]) + "\n")
                f.write("Threshold: " + str(threshold) + "\n")
                f.write("From: " + str(list(list(G.nodes())[0])) + "\n")
                f.write("BFS: " + str([list(dt) for dt in traverse]) + "\n")