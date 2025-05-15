import numpy as np
import os 

from generation.rb_tree.generation import RedBlackTree
from generation.rb_tree.utils import parse_rb_tree_file_serialized
from generation.binary_tree.tree_utils import lst_to_str

if __name__ == "__main__":
    path = "generation/rb_tree"
    os.makedirs(f"{path}/compound", exist_ok=True)

    for mode in ["easy", "medium", "hard"]:
        if mode == "easy":
            min_num_op, max_num_op = 5, 10
        elif mode == "medium":
            min_num_op, max_num_op = 11, 20
        else:
            min_num_op, max_num_op = 21, 30

        input_file = f"{path}/rbt_input_{mode}.txt"
        trees = parse_rb_tree_file_serialized(input_file)

        with open(f"{path}/construct_compound/rbt_construct_compound_{mode}.txt", "w") as f_write:
            for idx, tree in enumerate(trees):
                # track deletable values
                can_delete = tree.values.copy()
                mn = min(can_delete) if can_delete else 0
                mx = max(can_delete) if can_delete else 0
                can_insert = list(set(np.arange(mn, mx + 1)) - set(can_delete))

                f_write.write(f"Tree {idx}\n")

                num_op = np.random.randint(min_num_op, max_num_op + 1)
                for _ in range(num_op):
                    if can_delete and np.random.rand() < 0.5:
                        op = "delete"
                    else:
                        op = "insert"

                    if op == "insert" or not can_delete:
                        v = int(np.random.choice(can_insert))
                        tree.insert(v)
                        can_insert.remove(v)
                        can_delete.append(v)
                        f_write.write(f"Insert: {v}\n")
                    else:
                        v = int(np.random.choice(can_delete))
                        tree.delete(v)
                        can_delete.remove(v)
                        can_insert.append(v)
                        f_write.write(f"Delete: {v}\n")

                # now capture pre-order as [[value, color], ...]
                raw_pre = tree.preorder()                # [(v,c), …]
                pre_pairs = [[v, c] for v, c in raw_pre]

                f_write.write("Pre-order: ")
                if pre_pairs:
                    f_write.write(lst_to_str(pre_pairs))
                else:
                    f_write.write("[]")
                f_write.write("\n")
