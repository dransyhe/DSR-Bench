import numpy.random as random

from generation.binary_tree.bst_generation.bst_generation import BinarySearchTree
from generation.binary_tree.tree_utils import build_tree, lst_to_str, all_vals

if __name__ == "__main__":
    for mode in ["easy", "medium", "hard"]:
        path = "generation/binary_tree"
        with open(f"{path}/bst_generation/bst_input_{mode}.txt", "r") as f:
            f_write = open(f"{path}/traversal/bst_traversal_{mode}.txt", "w")

            i = 0
            lines = f.readlines()
            while i < len(lines):
                root = None
                tree, i = build_tree(lines, i, root)
                bst = BinarySearchTree()
                bst.root = tree
                bst.values = all_vals(tree)

                if tree is not None:
                    
                    node_to_insert = random.choice(bst.values)
                    
                    f_write.write("Pre-order: ")
                    f_write.write(lst_to_str(bst.preorder()))
                    f_write.write(" \n")
                    f_write.write("In-order: ")
                    f_write.write(lst_to_str(bst.inorder()))
                    f_write.write(" \n")
                    f_write.write("Post-order: ")
                    f_write.write(lst_to_str(bst.postorder()))
                    f_write.write(" \n")
                    f_write.write(f"Depth: {tree.depth()}\n")
                    f_write.write("\n")
