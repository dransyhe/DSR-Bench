import numpy as np

from generation.binary_tree.bst_generation.bst_generation import BinarySearchTree
from generation.binary_tree.tree_utils import build_tree, lst_to_str, all_vals

if __name__ == "__main__":
    for mode in ["easy", "medium", "hard"]:
        path = "generation/binary_tree"
        f_write = open(f"{path}/compound/bst_compound_{mode}.txt", "w")
        
        if mode == "easy":
            min_size = 5
            max_size = 10
        elif mode == "medium":
            min_size = 15
            max_size = 20
        else:
            min_size = 21
            max_size = 30
            
        for _ in range(30):
        
            bst = BinarySearchTree()
            
            num_ops = np.random.randint(min_size, max_size)
            for _ in range(num_ops):
                can_insert = list(set(np.arange(0, 100)) - set(bst.values))
                if np.random.rand() < 0.7 or bst.root is None:
                    insert_val = np.random.choice(can_insert)
                    bst.insert(insert_val)
                    f_write.write(f"Insert: {insert_val}\n")
                else:
                    delete_val = np.random.choice(bst.values)
                    bst.delete(delete_val)
                    f_write.write(f"Delete: {delete_val}\n")
            print(bst.preorder())
            f_write.write(lst_to_str(bst.preorder()))
            f_write.write(" \n")



