# All helper functions used by both random binary tree and BST are factored 
# here to avoid repetition

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

    def depth(self):
        left_depth = self.left.depth() if self.left else 0
        right_depth = self.right.depth() if self.right else 0
        return max(left_depth, right_depth) + 1
    
    
def build_tree(lines_iter, NIL):
    """
    Rebuilds a Red-Black Tree from an iterator over lines (preorder format).
    Returns the reconstructed root.
    """
    try:
        line = next(lines_iter).strip()
    except StopIteration:
        return NIL

    if line == "# NIL":
        return NIL

    value_str, color = line.split()
    node = Node(int(value_str), color=color)
    node.left = build_tree(lines_iter, NIL)
    if node.left != NIL:
        node.left.parent = node
    node.right = build_tree(lines_iter, NIL)
    if node.right != NIL:
        node.right.parent = node
    return node



def traverse_tree(root, f):
    if not root:
        return

    if root.left:
        left = root.left.value
    else:
        left = None
    if root.right:
        right = root.right.value
    else:
        right = None

    f.write(f"{root.value} {left} {right}\n")
    traverse_tree(root.left, f)
    traverse_tree(root.right, f)
    
def num_to_str(generated_list, f):
    """
    Converts a list of numbers to a string and writes it to input file f.
    """
    input = "["
    for num in generated_list[:-1]:
        input = input + str(num) + ","
    input = input + str(generated_list[-1]) + "]" + "\n"
    f.write(input)
    
def lst_to_str(lst):
    """
    Converts a list of numbers to a string.
    """
    input = "["
    for num in lst[:-1]:
        input = input + str(num) + ","
    input = input + str(lst[-1]) + "]"
    return input

def all_vals(node):
    """
    Returns all values in the tree rooted at node.
    """
    if node is None:
        return []
    return (
        [node.value]
        + all_vals(node.left)
        + all_vals(node.right)
    )