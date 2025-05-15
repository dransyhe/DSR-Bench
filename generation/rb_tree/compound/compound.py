import numpy as np
import os

from generation.rb_tree.generation import RedBlackTree
from generation.binary_tree.tree_utils import lst_to_str

if __name__ == "__main__":
    np.random.seed(0)  # reproducibility

    path = "generation/rb_tree"
    out_dir = f"{path}/compound"
    os.makedirs(out_dir, exist_ok=True)

    for mode in ["easy", "medium", "hard"]:
        if mode == "easy":
            min_num_op, max_num_op = 5, 10
            max_val = 100
        elif mode == "medium":
            min_num_op, max_num_op = 11, 20
            max_val = 100
        else:
            min_num_op, max_num_op = 21, 30
            max_val = 100

        with open(f"{out_dir}/rbt_compound_{mode}.txt", "w") as f_write:
            for idx in range(30):
                # start with an empty tree
                tree = RedBlackTree()
                can_delete = []
                # pool of all possible insert values
                pool = list(range(max_val + 1))
                np.random.shuffle(pool)
                can_insert = pool.copy()

                f_write.write(f"Tree {idx}\n")

                # choose how many operations to perform
                num_op = np.random.randint(min_num_op, max_num_op + 1)
                for _ in range(num_op):
                    # 70% chance to delete if possible, else insert
                    if can_delete and np.random.rand() < 0.3:
                        op = "delete"
                    else:
                        op = "insert"

                    if op == "insert":
                        # pick a unique random value to insert
                        v = int(np.random.choice(can_insert))
                        tree.insert(v)
                        can_delete.append(v)
                        f_write.write(f"Insert: {v}\n")
                    else:  # delete
                        # remove an existing value
                        v = int(np.random.choice(can_delete))
                        tree.delete(v)
                        can_delete.remove(v)
                        can_insert.append(v)
                        f_write.write(f"Delete: {v}\n")

                # output pre-order traversal as [[value, color], ...]
                raw_pre = tree.preorder()               # returns List[(value, color)]
                pre_pairs = [[v, c] for v, c in raw_pre]

                f_write.write("Pre-order: ")
                if pre_pairs:
                    f_write.write(lst_to_str(pre_pairs))
                else:
                    f_write.write("[]")
                f_write.write("\n")
