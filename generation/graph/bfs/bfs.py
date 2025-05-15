import networkx as nx
import random

def read_graphs_from_file(file_path):
    graphs = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        current_graph = None

        for line in lines:
            line = line.strip()
            if line.startswith("Graph"):
                if current_graph is not None:
                    graphs.append(current_graph)
                current_graph = nx.Graph()
            elif ',' not in line:  # Node list
                nodes = list(map(int, line.split()))
                current_graph.add_nodes_from(nodes)
            elif line:  # Edge list
                u, v = map(int, line.split(', '))
                current_graph.add_edge(u, v)

        # Append the last graph
        if current_graph is not None:
            graphs.append(current_graph)

    return graphs


def bfs_path_to_file(graphs, output_file):
    with open(output_file, 'w') as f:
        for i, G in enumerate(graphs):
            # Randomly select a source node
            nodes = list(G.nodes())
            source = random.sample(nodes, 1)[0]
            f.write(f"Graph {i}: Source = {source} \n")

            # Perform BFS and find a path
            try:
                bfs_edges = nx.bfs_edges(G, source=source, sort_neighbors=sorted)
                path = [source]
                for u, v in bfs_edges:
                    if v not in path:
                        path.append(v)
                f.write('[' + ', '.join(map(str, path)) + "]\n")
            except nx.NetworkXNoPath:
                f.write("none\n")


if __name__ == "__main__":
    
    for mode in ["easy", "medium", "hard"]:
        path = "generation/graph"
        input_file = f"{path}/graph_input_{mode}.txt"
        graphs = read_graphs_from_file(input_file)

        output_file = f"{path}/bfs/bfs_{mode}.txt"
        bfs_path_to_file(graphs, output_file)


