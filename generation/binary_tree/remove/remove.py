import numpy as np

from generation.binary_tree.bst_generation.bst_generation import BinarySearchTree
from generation.binary_tree.tree_utils import build_tree, lst_to_str, all_vals

if __name__ == "__main__":
    for mode in ["easy", "medium", "hard"]:
        path = "generation/binary_tree"
        with open(f"{path}/bst_generation/bst_input_{mode}.txt", "r") as f:
            f_write = open(f"{path}/remove/bst_remove_{mode}.txt", "w")

            i = 0
            lines = f.readlines()
            while i < len(lines):
                root = None
                tree, i = build_tree(lines, i, root)
                bst = BinarySearchTree()
                bst.root = tree
                bst.values = all_vals(bst.root)
                
                if tree is not None:
                    if len(bst.values) > 0:
                        delete_val = np.random.choice(bst.values)
                        print(bst.values)
                        print(delete_val)
                        bst.delete(delete_val)
                    else:
                        raise Exception("No values to remove, tree is empty (so something's wrong).")
                
                    f_write.write(f"Remove: {delete_val}\n")
                    f_write.write("Pre-order: ")
                    f_write.write(lst_to_str(bst.preorder()))
                    f_write.write(" \n")
                    f_write.write("Post-order: ")
                    f_write.write(lst_to_str(bst.postorder()))
                    f_write.write(" \n")



