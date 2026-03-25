"""
One-time script: generates rbt_construct_{mode}_tree.json for easy/medium/hard.

Each JSON file is a list of 30 nested-dict trees, one per problem in the
corresponding rbt_construct_{mode}.txt file.  The tree is rebuilt by re-inserting
the values (in the order listed in the txt file) into a fresh RedBlackTree, so
the result is guaranteed to match the pre-order ground truth already in the txt.

Run from the repo root:
    python -m generation.rb_tree.generate_tree_json
"""
import ast
import json
import os
import sys

# Allow running from repo root without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from generation.rb_tree.generation import RedBlackTree


def node_to_dict(node, NIL):
    """Recursively convert a RedBlackTree node to a nested dict."""
    if node is NIL or node.value is None:
        return None
    return {
        "value": int(node.value),
        "color": node.color,
        "left": node_to_dict(node.left, NIL),
        "right": node_to_dict(node.right, NIL),
    }


def generate_for_mode(mode):
    txt_path = f"generation/rb_tree/construct/rbt_construct_{mode}.txt"
    out_path = f"generation/rb_tree/construct/rbt_construct_{mode}_tree.json"

    trees = []
    with open(txt_path, "r") as f:
        for line in f:
            if line.startswith("Values:"):
                values = ast.literal_eval(line.split(":", 1)[1].strip())
                tree = RedBlackTree()
                for v in values:
                    tree.insert(v)
                trees.append(node_to_dict(tree.root, tree.NIL))

    with open(out_path, "w") as f:
        json.dump(trees, f, indent=2)
    print(f"Wrote {len(trees)} trees to {out_path}")


if __name__ == "__main__":
    for mode in ["easy", "medium", "hard"]:
        generate_for_mode(mode)
