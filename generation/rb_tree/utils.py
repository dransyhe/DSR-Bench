from generation.rb_tree.generation import Node, RedBlackTree


def build_tree_serialized(lines_iterator, NIL):
    """
    Reconstruct a tree from a serialized pre-order traversal.
    It consumes lines from the iterator. When a '#' is encountered,
    it represents a NIL node.
    
    Args:
        lines_iterator (iterator): An iterator over lines of the serialized tree.
        NIL (Node): The sentinel NIL node to use.
        
    Returns:
        Node: The root node of the reconstructed tree.
    """
    try:
        line = next(lines_iterator).strip()
    except StopIteration:
        return NIL

    if line == "#":
        return NIL

    parts = line.split()
    if len(parts) < 2:
        return NIL  # malformed line
    value = int(parts[0])
    color = parts[1]
    node = Node(value, color)
    # Recursively build the left and right subtrees.
    node.left = build_tree_serialized(lines_iterator, NIL)
    if node.left != NIL:
        node.left.parent = node
    node.right = build_tree_serialized(lines_iterator, NIL)
    if node.right != NIL:
        node.right.parent = node
    return node

def parse_rb_tree_file_serialized(filepath):
    """
    Parse a file containing multiple trees in serialized format.
    
    The file format is expected to be:
    
        Tree 0
        (serialized tree: one line per node or '#' for NIL)
        Tree 1
        (serialized tree)
        ...
    
    Returns:
        List[RedBlackTree]: A list of reconstructed RedBlackTree objects.
    """
    trees = []
    with open(filepath, "r") as f:
        lines = f.readlines()

    # Use an iterator to read through the lines.
    lines_iter = iter(lines)
    while True:
        try:
            header = next(lines_iter).strip()
        except StopIteration:
            break  # End of file reached.
        if not header.startswith("Tree"):
            continue  # Skip any unexpected lines.
        # Create a new tree and build it from the subsequent lines.
        tree = RedBlackTree()
        tree.root = build_tree_serialized(lines_iter, tree.NIL)
        tree.values = [int(node[0]) for node in tree.inorder()]
        trees.append(tree)
    return trees

def describe_tree_natural(root, NIL):
    """
    Generate a natural language description for the tree.
    Every relationship is stated with the parent's value.
    For example, "58's left child is 5 (black)" or "58's right child is none."
    Returns a list of description lines.
    """
    descriptions = []
    if root == NIL or root is None:
        return ["The tree is empty."]
    
    # Describe the root.
    color_text = "black" if root.color == "b" else "red"
    descriptions.append(f"The root is {root.value} ({color_text}).")
    
    def process_node(node):
        if node == NIL or node is None:
            return
        
        # Describe left child.
        if node.left == NIL or node.left.value is None:
            descriptions.append(f"{node.value}'s left child is none.")
        else:
            left_color = "black" if node.left.color == "b" else "red"
            descriptions.append(f"{node.value}'s left child is {node.left.value} ({left_color}).")
        # Describe right child.
        if node.right == NIL or node.right.value is None:
            descriptions.append(f"{node.value}'s right child is none.")
        else:
            right_color = "black" if node.right.color == "b" else "red"
            descriptions.append(f"{node.value}'s right child is {node.right.value} ({right_color}).")
        
        # Process the children recursively.
        process_node(node.left)
        process_node(node.right)
    
    process_node(root)
    return descriptions

def convert_file_to_natural_language_description(filepath):
    """
    Reads a file containing one or more serialized red-black trees and returns a list of
    natural language descriptions (one description per tree).
    
    File format is assumed to be:
    
        Tree 0
        (serialized tree: one line per node or '#' for NIL)
        Tree 1
        (serialized tree)
        ...
    """
    tree_descriptions = []
    with open(filepath, "r") as f:
        lines = f.readlines()

    lines_iter = iter(lines)
    while True:
        try:
            header = next(lines_iter).strip()
        except StopIteration:
            break  # end of file
        
        # Skip lines that don't start with "Tree"
        if not header.startswith("Tree"):
            continue

        tree_label = header  # e.g., "Tree 0"
        # Create a new NIL sentinel for this tree.
        NIL = Node(value=None, color="b")
        tree_root = build_tree_serialized(lines_iter, NIL)
        descriptions = describe_tree_natural(tree_root, NIL)
        # Combine header and description lines.
        full_description = tree_label + "\n" + "\n".join(descriptions)
        tree_descriptions.append(full_description)
    
    return tree_descriptions

# ----------------------------------------------------------------------------
# Main block: parsing 30 trees for each mode
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    for mode in ["easy"]:
        path = "generation/rb_tree"
        input_file = f"{path}/rbt_input_{mode}.txt"
        trees = parse_rb_tree_file_serialized(input_file)
        print(f"Mode: {mode}")
        print(convert_file_to_natural_language_description(input_file))