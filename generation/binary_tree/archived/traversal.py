# def num_to_str(generated_list, f):
#     input = "["
#     for num in generated_list[:-1]:
#         input = input + str(num) + ","
#     input = input + str(generated_list[-1]) + "]" + "\n"
#     f.write(input)

import random
from generation.binary_tree.tree_utils import build_tree, num_to_str

# class Node:
#     def __init__(self, value):
#         self.value = value
#         self.left = None
#         self.right = None

#     def depth(self):
#         left_depth = self.left.depth() if self.left else 0
#         right_depth = self.right.depth() if self.right else 0
#         return max(left_depth, right_depth) + 1


# def build_tree(lines, i, root):
#     i += 1
#     if i >= len(lines) or "Tree" in lines[i]:
#         return root, i

#     root, left, right = lines[i][:-1].split(" ")
#     # print(root, left, right)
#     left_child = None
#     if "None" not in left:
#         left_child, i = build_tree(lines, i, left_child)
#     right_child = None
#     if "None" not in right:
#         right_child, i = build_tree(lines, i, right_child)

#     root = Node(int(root))
#     root.left = left_child
#     root.right = right_child
#     return root, i


def print_tree(node, level, f):
    if node is not None:
        print_tree(node.right, level + 1, f)
        f.write(" " * 4 * level + f"-> {node.value}\n")
        print_tree(node.left, level + 1, f)

def preorder(root, f):
    # If the root is None
    if not root:
        return

    # Using tree-node type stack STL
    stack = []

    nodes = []

    while root or stack:
        if root:
            # Print the root
            f.write(f"{root.value} ")
            nodes += [root.value]

            # Push the node in the stack
            stack.append(root)

            # Move to left subtree
            root = root.left
        else:
            # Remove the top of stack
            root = stack.pop()
            root = root.right

    f.write("\n")
    return nodes


def inorder(root, f):
    # If root is NULL
    if root is None:
        return

    # Recursively call for the left
    # and the right subtree
    inorder(root.left, f)
    f.write(f"{root.value} ")
    inorder(root.right, f)


def postorder(node, f):
    if node == None:
        return

    # First recur on left subtree
    postorder(node.left, f)

    # Then recur on right subtree
    postorder(node.right, f)

    # Now deal with the node
    f.write(f"{node.value} ")


for mode in ["easy", "medium", "hard"]:
    path = "generation/binary_tree"
    with open(f"{path}/array_input_{mode}.txt", "r") as f:
        f_write = open(f"traversal_{mode}.txt", "w")

        i = 0
        lines = f.readlines()
        while i < len(lines):
            root = None
            tree, i = build_tree(lines, i, root)
            # print_tree(tree, 0, f_write)
            if tree is not None:
                # print_tree(tree, 0, f_write)
                f_write.write("Pre-order: ")
                nodes = preorder(tree, f_write)
                f_write.write("In-order: ")
                inorder(tree, f_write)
                f_write.write(" \n")
                f_write.write("Post-order: ")
                postorder(tree, f_write)
                f_write.write(" \n")
                f_write.write(f"Depth: {tree.depth()}\n")






