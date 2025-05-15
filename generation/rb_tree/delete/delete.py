import numpy as np

from generation.rb_tree.generation import RedBlackTree
from generation.rb_tree.utils import parse_rb_tree_file_serialized
from generation.binary_tree.tree_utils import lst_to_str

if __name__ == "__main__":
    for mode in ["easy", "medium", "hard"]:
        path = "generation/rb_tree"
        input_file = f"{path}/rbt_input_{mode}.txt"
        trees = parse_rb_tree_file_serialized(input_file)
        print(f"Mode: {mode}")
        with open(f"{path}/rbt_input_{mode}.txt", "r") as f:
            f_write = open(f"{path}/delete/rbt_delete_{mode}.txt", "w")
            for idx, tree in enumerate(trees):
                can_delete = tree.values
                
                if len(can_delete) > 0:
                    delete_val = np.random.choice(can_delete)
                    tree.delete(delete_val)
                else:
                    raise Exception("No values to delete, tree is empty?")
                
                pre = tree.preorder()
                post = tree.postorder()
                pre_vals = [x[0] for x in pre]
                post_vals = [x[0] for x in post]
                pre_colors = [x[1] for x in pre]
                post_colors = [x[1] for x in post]

                f_write.write(f"Delete: {delete_val}\n")
                f_write.write("Pre-order: ")
                f_write.write(lst_to_str(pre_vals))
                f_write.write(" \n")
                f_write.write("Pre-color: ")
                f_write.write(lst_to_str(pre_colors))
                f_write.write(" \n")
                f_write.write("Post-order: ")
                f_write.write(lst_to_str(post_vals))
                f_write.write(" \n")
                f_write.write("Post-color: ")
                f_write.write(lst_to_str(post_colors))
                f_write.write(" \n")