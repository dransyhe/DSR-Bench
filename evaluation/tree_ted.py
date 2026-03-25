"""
Generic tree-edit distance (TED) utilities for DSR-Bench.

Trees are represented as nested dicts:
  {"value": <any>, "color": <str>, "left": <dict|None>, "right": <dict|None>}

The node label used for TED encodes both value and color, so the distance is
sensitive to structural errors AND attribute errors.

Score is in [0, 1]:
  1.0  = perfect match (TED == 0)
  0.0  = maximally different (TED >= size_pred + size_truth)

Normalization: score = max(0, 1 - TED / (size_pred + size_truth))
This upper-bounds TED because every edit path goes through an empty tree.
"""
import zss


def _rb_label(d):
    return f"{d['value']}:{d['color']}"

def _kdt_label(d):
    return str(d['point'])

def _dict_to_zss(d, label_fn):
    """Convert a nested dict to a zss.Node. Returns None for null subtrees."""
    if d is None:
        return None
    node = zss.Node(label_fn(d))
    left = _dict_to_zss(d.get("left"), label_fn)
    right = _dict_to_zss(d.get("right"), label_fn)
    if left is not None:
        node.addkid(left)
    if right is not None:
        node.addkid(right)
    return node


def _tree_size(d):
    if d is None:
        return 0
    return 1 + _tree_size(d.get("left")) + _tree_size(d.get("right"))


def ted_score(pred_dict, truth_dict, label_fn=_rb_label):
    """
    Compute normalized TED score in [0, 1].
    pred_dict / truth_dict are nested dicts with keys left, right, and whatever
    label_fn extracts from a node. Defaults to RB-tree labeling (value + color).
    Returns 0.0 on any parsing/computation failure.
    """
    if pred_dict is None:
        return 0.0
    try:
        pred_node = _dict_to_zss(pred_dict, label_fn)
        truth_node = _dict_to_zss(truth_dict, label_fn)
        distance = zss.simple_distance(pred_node, truth_node)
        max_edits = _tree_size(pred_dict) + _tree_size(truth_dict)
        if max_edits == 0:
            return 1.0
        return max(0.0, 1.0 - distance / max_edits)
    except Exception:
        return 0.0
