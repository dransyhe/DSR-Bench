#!/usr/bin/env python3
import os
import random
import networkx as nx
from collections import deque

# ── CONFIG ───────────────────────────────────────────────────────────────────────
module_dir   = "./natural/graph/"
os.makedirs(module_dir, exist_ok=True)

mode = "hard"

natural_path = os.path.join(module_dir, f"natural-{mode}.txt")

NUM_INSTANCES = 30
if mode == "easy":
    MIN_NODES, MAX_NODES = 5, 10
elif mode == "medium":
    MIN_NODES, MAX_NODES = 11, 20
else:
    MIN_NODES, MAX_NODES = 21, 30
EDGE_PROB = 0.3  # p for Erdos–Rényi

# planet names (50 total)
planets = [
    "Aegis", "Arcadia", "Bellatrix", "Boreas", "Cetus",
    "Corvus", "Deneb", "Draco", "Elara", "Elysia",
    "Fomalhaut", "Fenrir", "Ganymede", "Gaia", "Helios",
    "Hyperion", "Icarus", "Io", "Janus", "Juno",
    "Kelvin", "Krypton", "Levania", "Luna", "Midas",
    "Miranda", "Nereus", "Nova", "Oberon", "Orion",
    "Phoebe", "Pulsar", "Quasar", "Rigel", "Rhea",
    "Selene", "Styx", "Triton", "Titan", "Umbra",
    "Umbriel", "Vega", "Winona", "Wraith", "Xandar",
    "Xenon", "Ymir", "Yavin", "Zephyr", "Zebes"
]

# ── TRAVERSAL ─────────────────────────────────────────────────────────────────────
def dfs_full(G, source):
    """Return DFS preorder starting at source (neighbors sorted lexically)."""
    visited, order = set(), []
    def dfs(u):
        visited.add(u)
        order.append(u)
        for v in sorted(G.adj[u]):
            if v not in visited:
                dfs(v)
    dfs(source)
    return order

# ── I/O ──────────────────────────────────────────────────────────────────────────
def write_block(f, **kwargs):
    for k, v in kwargs.items():
        f.write(f"{k}: {v}\n")
    f.write("\n")

with open(natural_path, "w") as fl:
    for _ in range(NUM_INSTANCES):
        # 1) pick some planet-names
        n = random.randint(MIN_NODES, MAX_NODES)
        nodes = random.sample(planets, n)

        # 2) generate an ER graph on n unnamed nodes
        G = nx.erdos_renyi_graph(n, EDGE_PROB)

        # 3) relabel 0…n-1 → your planet names
        mapping = {i: nodes[i] for i in G.nodes()}
        G = nx.relabel_nodes(G, mapping)

        # 4) pick a source
        source = random.choice(nodes)

        # 5) run DFS from source (only its connected component)
        traversal = dfs_full(G, source)

        # 6) dump
        write_block(fl,
            nodes=nodes,
            edges=list(G.edges()),
            source=source,
            traversal=traversal
        )
