"""
Generate nested-JSON ground-truth files for KD-tree TED evaluation.

For each construct_{dim}d/construct_{mode}.txt, reads the Points lines,
rebuilds the KDTree, and writes construct_{dim}d/construct_{mode}_tree.json
as a list of nested dicts: {"point": [...], "left": {...}|null, "right": {...}|null}.

Usage (from repo root):
    python -m generation.kd_tree.generate_tree_json
"""
import ast
import json
import os
import numpy as np

from generation.kd_tree.generation import KDTree


def node_to_dict(node):
    if node is None:
        return None
    return {
        "point": node.value.tolist() if hasattr(node.value, "tolist") else list(node.value),
        "left": node_to_dict(node.left),
        "right": node_to_dict(node.right),
    }


if __name__ == "__main__":
    for dim in [1, 2, 3, 5]:
        for mode in ["easy", "medium", "hard"]:
            input_path = f"generation/kd_tree/construct_{dim}d/construct_{mode}.txt"
            output_path = f"generation/kd_tree/construct_{dim}d/construct_{mode}_tree.json"
            if not os.path.exists(input_path):
                continue
            trees = []
            with open(input_path) as f:
                for line in f:
                    if line.startswith("Points:"):
                        points = np.array(ast.literal_eval(line.split(":", 1)[1].strip()))
                        tree = KDTree(points)
                        trees.append(node_to_dict(tree.root))
            with open(output_path, "w") as f:
                json.dump(trees, f)
            print(f"Wrote {len(trees)} trees to {output_path}")
