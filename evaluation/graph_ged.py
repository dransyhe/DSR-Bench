"""
Graph edit distance (GED) utilities for DSR-Bench.

Graphs are represented as dicts:
  {"nodes": [[x1, y1, ...], ...], "edges": [[[x1,y1],[x2,y2]], ...]}

GED is computed as the symmetric difference of edge sets. Node coordinates
are rounded to 2 decimal places to avoid floating-point noise from the LLM.
Edges are stored as frozensets so (A-B) == (B-A) for undirected graphs.

Score is in [0, 1]:
  1.0  = perfect match (GED == 0)
  0.0  = maximally different (GED >= |E_pred| + |E_truth|)

Normalization: score = max(0, 1 - GED / (|E_pred| + |E_truth|))
"""


def _edge_set(graph):
    edges = set()
    for edge in graph.get("edges", []):
        u = tuple(round(x, 2) for x in edge[0])
        v = tuple(round(x, 2) for x in edge[1])
        edges.add(frozenset([u, v]))
    return edges


def ged_score(pred_graph, truth_graph):
    """
    Compute normalized GED score in [0, 1] based on symmetric edge difference.
    pred_graph / truth_graph are dicts with keys "nodes" and "edges".
    Returns 0.0 on any parsing/computation failure.
    """
    if pred_graph is None:
        return 0.0
    try:
        pred_edges = _edge_set(pred_graph)
        truth_edges = _edge_set(truth_graph)
        ged = len(pred_edges.symmetric_difference(truth_edges))
        max_edits = len(pred_edges) + len(truth_edges)
        if max_edits == 0:
            return 1.0
        return max(0.0, 1.0 - ged / max_edits)
    except Exception:
        return 0.0
