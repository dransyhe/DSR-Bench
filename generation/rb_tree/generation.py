import numpy.random as random
from generation.binary_tree.tree_utils import lst_to_str
import os

random.seed(0)  # For reproducibility

class Node:
    def __init__(self, value, color='r', parent=None, left=None, right=None):
        self.value = value
        self.color = color  # 'r' or 'b'
        self.parent = parent
        self.left = left
        self.right = right


class RedBlackTree:
    def __init__(self):
        self.NIL = Node(value=None, color='b')  # Sentinel node
        self.root = self.NIL
        self.values = []

    def insert(self, value):
        self.values.append(value)
        new_node = Node(value, color='r', left=self.NIL, right=self.NIL)
        parent = None
        current = self.root

        while current != self.NIL:
            parent = current
            if new_node.value < current.value:
                current = current.left
            else:
                current = current.right

        new_node.parent = parent
        if parent is None:
            self.root = new_node
        elif new_node.value < parent.value:
            parent.left = new_node
        else:
            parent.right = new_node

        self._fix_insert(new_node)
        
    def _fix_insert(self, node):
        while node != self.root and node.parent.color == 'r':
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle.color == 'r':
                    node.parent.color = 'b'
                    uncle.color = 'b'
                    node.parent.parent.color = 'r'
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self._rotate_left(node)
                    node.parent.color = 'b'
                    node.parent.parent.color = 'r'
                    self._rotate_right(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                if uncle.color == 'r':
                    node.parent.color = 'b'
                    uncle.color = 'b'
                    node.parent.parent.color = 'r'
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        node = node.parent
                        self._rotate_right(node)
                    node.parent.color = 'b'
                    node.parent.parent.color = 'r'
                    self._rotate_left(node.parent.parent)

        self.root.color = 'b'
        
    def delete(self, value):
        node = self._search(self.root, value)
        if node == self.NIL:
            return  # Node not found

        y = node
        y_original_color = y.color
        if node.left == self.NIL:
            x = node.right
            self._transplant(node, node.right)
        elif node.right == self.NIL:
            x = node.left
            self._transplant(node, node.left)
        else:
            y = self._minimum(node.right)
            y_original_color = y.color
            x = y.right
            if y.parent == node:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = node.right
                y.right.parent = y
            self._transplant(node, y)
            y.left = node.left
            y.left.parent = y
            y.color = node.color

        if y_original_color == 'b':
            self._fix_delete(x)
            
    def _fix_delete(self, x):
        while x != self.root and x.color == 'b':
            if x == x.parent.left:
                sibling = x.parent.right
                if sibling.color == 'r':
                    sibling.color = 'b'
                    x.parent.color = 'r'
                    self._rotate_left(x.parent)
                    sibling = x.parent.right
                if sibling.left.color == 'b' and sibling.right.color == 'b':
                    sibling.color = 'r'
                    x = x.parent
                else:
                    if sibling.right.color == 'b':
                        sibling.left.color = 'b'
                        sibling.color = 'r'
                        self._rotate_right(sibling)
                        sibling = x.parent.right
                    sibling.color = x.parent.color
                    x.parent.color = 'b'
                    sibling.right.color = 'b'
                    self._rotate_left(x.parent)
                    x = self.root
            else:
                sibling = x.parent.left
                if sibling.color == 'r':
                    sibling.color = 'b'
                    x.parent.color = 'r'
                    self._rotate_right(x.parent)
                    sibling = x.parent.left
                if sibling.left.color == 'b' and sibling.right.color == 'b':
                    sibling.color = 'r'
                    x = x.parent
                else:
                    if sibling.left.color == 'b':
                        sibling.right.color = 'b'
                        sibling.color = 'r'
                        self._rotate_left(sibling)
                        sibling = x.parent.left
                    sibling.color = x.parent.color
                    x.parent.color = 'b'
                    sibling.left.color = 'b'
                    self._rotate_right(x.parent)
                    x = self.root
        x.color = 'b'
        
    def _transplant(self, u, v):
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent
        
    def _search(self, node, value):
        while node != self.NIL and value != node.value:
            if value < node.value:
                node = node.left
            else:
                node = node.right
        return node

    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def inorder(self, node=None):
        if node is None:
            node = self.root
        if node == self.NIL:
            return []
        return (self.inorder(node.left) +
                [(node.value, node.color)] +
                self.inorder(node.right))
        
    def preorder(self, node=None):
        if node is None:
            node = self.root
        if node == self.NIL:
            return []
        return [(node.value, node.color)] + self.preorder(node.left) + self.preorder(node.right)
    
    def _minimum(self, node):
        while node.left != self.NIL:
            node = node.left
        return node


def write_tree_to_file_serialized(node, f, NIL):
    """
    Write a tree in pre-order to a file, using '#' to mark NIL nodes.
    Args:
        node (Node): Current node in the tree.
        f (file object): Open file to write to.
        NIL (Node): The sentinel NIL node.
    """
    if node == NIL or node.value is None:
        f.write("#\n")
        return
    f.write(f"{node.value} {node.color}\n")
    write_tree_to_file_serialized(node.left, f, NIL)
    write_tree_to_file_serialized(node.right, f, NIL)


if __name__ == "__main__":
    path = "generation/rb_tree"
    os.makedirs(f"{path}/construct", exist_ok=True)

    # Generate raw serialized trees (optional)
    for mode in ["easy", "medium", "hard"]:
        with open(f"{path}/rbt_input_{mode}.txt", "w") as f:
            if mode == "easy":
                min_size, max_size = 5, 10
            elif mode == "medium":
                min_size, max_size = 11, 20
            else:
                min_size, max_size = 21, 30

            for k in range(30):
                f.write(f"Tree {k}\n")
                size = random.randint(min_size, max_size)
                tree = RedBlackTree()
                values = random.choice(100, size, replace=False)
                for v in values:
                    tree.insert(v)
                write_tree_to_file_serialized(tree.root, f, tree.NIL)

    # Generate construct files with only pre-order [value, color]
    for mode in ["easy", "medium", "hard"]:
        lst_values = []
        pre_pair_lst = []

        # First, regenerate the trees to capture values and preorders
        for k in range(30):
            size = random.randint(
                5 if mode=="easy" else 11 if mode=="medium" else 21,
                10 if mode=="easy" else 20 if mode=="medium" else 30
            )
            tree = RedBlackTree()
            values = random.choice(100, size, replace=False)
            lst_values.append(values)
            for v in values:
                tree.insert(v)
            raw_pre = tree.preorder()                     # [(v,c), …]
            pre_pair_lst.append([[v, c] for v, c in raw_pre])

        # Now write the construct file
        with open(f"{path}/construct/rbt_construct_{mode}.txt", "w") as f:
            for k in range(30):
                f.write(f"Tree {k}\n")
                f.write(f"Values: {lst_to_str(lst_values[k])}\n")
                f.write(f"Pre-order: {lst_to_str(pre_pair_lst[k])}\n")
