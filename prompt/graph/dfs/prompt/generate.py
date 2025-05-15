import random
import networkx as nx

def generate_random_graph():
    num_nodes = 5
    edge_prob = 0.5
    G = nx.erdos_renyi_graph(num_nodes, edge_prob)
    
    node_labels = {i: random.randint(0, 100) for i in range(num_nodes)}
    relabeled_G = nx.relabel_nodes(G, node_labels)
    nodes = sorted(list(relabeled_G.nodes))  # Ensure nodes are sorted
    edges = list(relabeled_G.edges)
    
    return nodes, edges

def dfs_recursive(node, adjacency_list, visited, dfs_order, steps):
    if node in visited:
        return
    
    visited.add(node)
    dfs_order.append(node)
    steps.append(f"Visiting node {node}. Current DFS path: {dfs_order}.")
    
    sorted_neighbors = sorted(adjacency_list[node])
    visited_neighbors = [neighbor for neighbor in sorted_neighbors if neighbor in visited]
    steps.append(f"It has neighbors {sorted(adjacency_list[node])}, and {visited_neighbors} are visited.")
    for neighbor in sorted(adjacency_list[node]):  # Visit smallest neighbor first
        if neighbor not in visited:
            steps.append(f"Going deeper from {node} to {neighbor}.")
            dfs_recursive(neighbor, adjacency_list, visited, dfs_order, steps)
    steps.append(f"Backtracking from {node}.")

def dfs_path(graph, start_node):
    nodes, edges = graph
    adjacency_list = {node: [] for node in nodes}
    for u, v in edges:
        adjacency_list[u].append(v)
        adjacency_list[v].append(u)
    
    for node in adjacency_list:
        adjacency_list[node].sort()  # Ensure smallest neighbor is visited first
    
    visited = set()
    dfs_order = []
    steps = [f"Starting depth-first search (DFS) from node {start_node}."]
    dfs_recursive(start_node, adjacency_list, visited, dfs_order, steps)
    steps.append(f"DFS complete. The final DFS path is {dfs_order}.")
    
    return dfs_order, steps

def generate_question():
    nodes, edges = generate_random_graph()
    start_node = random.choice(nodes)  # Randomly pick a start node
    dfs_result, steps = dfs_path((nodes, edges), start_node)
    
    question_template = f"""
    Q: The graph consists of nodes {nodes}, and edges {edges}.
    What is the depth-first search path starting from node {start_node}?
    """
    
    answer_template = "\n".join(steps)
    
    return f"{question_template}\nA: {answer_template}".strip()

if __name__ == "__main__":
    print(generate_question())