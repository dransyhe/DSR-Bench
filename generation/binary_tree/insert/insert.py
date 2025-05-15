import numpy as np

from generation.binary_tree.bst_generation.bst_generation import BinarySearchTree
from generation.binary_tree.tree_utils import build_tree, lst_to_str, all_vals

if __name__ == "__main__":
    for mode in ["easy", "medium", "hard"]:
        path = "generation/binary_tree"
        with open(f"{path}/bst_generation/bst_input_{mode}.txt", "r") as f:
            f_write = open(f"{path}/insert/bst_insert_{mode}.txt", "w")

            i = 0
            lines = f.readlines()
            while i < len(lines):
                root = None
                tree, i = build_tree(lines, i, root)
                bst = BinarySearchTree()
                bst.root = tree
                bst.values = all_vals(bst.root)
                
                if tree is not None:
                    min, max = bst.min_value(), bst.max_value()
                    can_insert = list(set(np.arange(min, max + 1)) - set(bst.values))
                  
                    if len(can_insert) > 0:
                        insert_val = np.random.choice(can_insert)
                        bst.insert(insert_val)
                    else:
                        raise Exception("No values to insert, something's wrong with values generated.")
                
                    f_write.write(f"Insert: {insert_val}\n")
                    f_write.write("Pre-order: ")
                    f_write.write(lst_to_str(bst.preorder()))
                    f_write.write(" \n")
                    f_write.write("Post-order: ")
                    f_write.write(lst_to_str(bst.postorder()))
                    f_write.write(" \n")



