import random
from collections import deque
import networkx as nx

def generate_random_graph():
    num_nodes = 5
    edge_prob = 0.5
    G = nx.erdos_renyi_graph(num_nodes, edge_prob)
    
    node_labels = {i: random.randint(0, 100) for i in range(num_nodes)}
    relabeled_G = nx.relabel_nodes(G, node_labels)
    nodes = list(relabeled_G.nodes)
    edges = list(relabeled_G.edges)
    
    return nodes, edges

def bfs_path(graph, start_node):
    nodes, edges = graph
    adjacency_list = {node: [] for node in nodes}
    for u, v in edges:
        adjacency_list[u].append(v)
        adjacency_list[v].append(u)
    
    for node in adjacency_list:
        adjacency_list[node].sort()  # Ensure smallest neighbor is visited first

    print(adjacency_list)
    
    queue = deque([start_node])
    visited = set([start_node])
    bfs_order = []
    steps = []
    
    while queue:
        node = queue.popleft()
        bfs_order.append(node)
        
        neighbors = [n for n in adjacency_list[node] if n not in visited]
        if neighbors:
            neighbors.sort()
            queue.extend(neighbors)
            visited.update(neighbors)
        
        steps.append(f"Next, we move onto node {node}, whose neighbors are {adjacency_list[node]} in ascending order. \n"
                     f"Since we have visited {sorted(visited)}, we remove {node} and add {neighbors}. The queue is now {list(queue)}.")
    
    return bfs_order, steps

def generate_question():
    nodes, edges = generate_random_graph()
    start_node = random.choice(nodes)  # Randomly pick a start node
    bfs_result, steps = bfs_path((nodes, edges), start_node)
    
    question_template = f"""
    Q: The graph consists of nodes {nodes}, and edges {edges}.
    What is the breadth-first search path starting from node {start_node}?
    """
    
    answer_template = "\n".join(steps) + f"\nThe queue is now empty, so we stop the traversal.\nThe final bfs path is {bfs_result}."
    
    return f"{question_template}\nA: {answer_template}".strip()

if __name__ == "__main__":
    print(generate_question())