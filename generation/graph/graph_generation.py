import random
import numpy as np
import networkx as nx 

for mode in ["easy", "medium", "hard"]:
    path = "generation/graph"
    with open(f"{path}/graph_input_{mode}.txt", "w") as f:
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
            G = nx.erdos_renyi_graph(n, edge_prob)
            
            numbers = random.sample(range(1, 100), n)
            node_mapping = {node: numbers[node] for node in G.nodes()}
            H = nx.relabel_nodes(G, node_mapping, copy=True)
            node_list = " ".join([str(v) for v in H.nodes()]) + "\n"  
            f.write(node_list)
            for u, v in H.edges():
                f.write(f"{u}, {v}\n")
            
