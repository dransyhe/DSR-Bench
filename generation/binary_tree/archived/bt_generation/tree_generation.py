import random
from tree_utils import Node, traverse_tree, num_to_str

def generate_random_binary_tree(size, available):
    if size == 0:
        return None

    # Choose random sizes for left and right subtrees
    left_size = random.randint(0, size - 1)
    right_size = size - 1 - left_size

    # Generate left and right subtrees recursively
    left_subtree = generate_random_binary_tree(left_size, available)
    right_subtree = generate_random_binary_tree(right_size, available)

    # Create new node with random value
    n = len(available)
    if n > 1:
        root = random.randint(0, n - 1)
    else:
        root = 0
    root = available[root]
    available.remove(root)
    root = Node(root)

    # Assign left and right subtrees to children
    root.left = left_subtree
    root.right = right_subtree

    return root


def print_tree(node, level, f):
    if node is not None:
        print_tree(node.right, level + 1, f)
        f.write(" " * 4 * level + f"-> {node.value}\n")
        print_tree(node.left, level + 1, f)



for mode in ["easy", "medium", "hard"]:
    with open(f"array_input_{mode}.txt", "w") as f:
        if mode == "easy":
            n = 10
            min_length = 4
            max_length = 7
        elif mode == "medium":
            n = 32
            min_length = 16
            max_length = 31
        else:
            n = 64
            min_length = 32
            max_length = 63

        for k in range(30):
            f.write(f"Tree {k}\n")
            size = random.randint(min_length, max_length)
            available = [random.randint(0, 100) for _ in range(n)]
            tree = generate_random_binary_tree(size, available)
            traverse_tree(tree, f)
            # print_tree(tree, level=0, f=f)

