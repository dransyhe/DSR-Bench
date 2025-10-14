from generation.binary_tree.tree_utils import traverse_tree
import numpy.random as random

class Node:
    """
    A node in the binary search tree.
    
    Attributes:
        val (int): The value stored in the node.
        left (Node): The left child of the node.
        right (Node): The right child of the node.
    """
    def __init__(self, val):
        self.value = val
        self.left = None
        self.right = None


class BinarySearchTree:
    """
    A binary search tree implementation.
    """
    def __init__(self, values=None):
        """Initialize the BST with an empty root."""
        self.root = None
        if values == None:
            self.values = []
    
    def insert(self, val):
        """
        Insert a new node with the given value into the BST.
        
        :param val: Value to be inserted.
        """
        if self.root is None:
            self.root = Node(val)
        else:
            self._insert(self.root, val)
        self.values.append(val)

    def _insert(self, current, val):
        """
        Helper method to recursively insert a new value starting from a given node.
        
        :param current: Current node in the tree.
        :param val: Value to be inserted.
        """
        if val < current.value:
            if current.left is None:
                current.left = Node(val)
            else:
                self._insert(current.left, val)
        else:  # Assuming duplicates go to the right, you can change this logic as needed
            if current.right is None:
                current.right = Node(val)
            else:
                self._insert(current.right, val)

    def search(self, val):
        """
        Search for a node with the given value in the BST.
        
        :param val: Value to search for.
        :return: True if the value exists in the BST, otherwise False.
        """
        return self._search(self.root, val)

    def _search(self, current, val):
        """
        Helper method to recursively search for a value starting from a given node.
        
        :param current: Current node in the tree.
        :param val: Value to search for.
        :return: True if the value is found, otherwise False.
        """
        if current is None:
            return False
        if val == current.value:
            return True
        elif val < current.value:
            return self._search(current.left, val)
        else:
            return self._search(current.right, val)

    def delete(self, val):
        """
        Delete a node with the given value from the BST, if it exists.
        
        :param val: Value of the node to delete.
        """
        self.root = self._delete(self.root, val)
        self.values.remove(val)

    def _delete(self, current, val):
        """
        Helper method to recursively delete a value starting from a given node.
        
        :param current: Current node in the tree.
        :param val: Value of the node to delete.
        :return: The new root of the subtree.
        """
        if current is None:
            return current
        
        # Traverse the tree to find the node to delete
        if val < current.value:
            current.left = self._delete(current.left, val)
        elif val > current.value:
            current.right = self._delete(current.right, val)
        else:
            # current node is the node to be deleted

            # Case 1: No child or only right child
            if current.left is None:
                temp = current.right
                current = None
                return temp

            # Case 2: Only left child
            elif current.right is None:
                temp = current.left
                current = None
                return temp

            # Case 3: Node with two children
            # Get the smallest value in the right subtree (in-order successor)
            temp = self._min_value_node(current.right)
            current.value = temp.value
            # Delete the in-order successor
            current.right = self._delete(current.right, temp.value)
        
        return current
    
    def depth(self):
        """
        Returns the depth of the BST.
        """
        return self._depth(self.root)
    
    def _depth(self, node):
        """
        Helper method to calculate the depth of the BST.
        """
        if node is None:
            return -1
        left_depth = self._depth(node.left)
        right_depth = self._depth(node.right)
        return max(left_depth, right_depth) + 1
    
    def min_value(self):
        """
        Returns the minimum value in the BST.
        """
        return self._min_value_node(self.root).value
    
    def _min_value_node(self, node):
        """
        Helper method to find the node with the minimum value in the BST.
        """
        current = node
        while current.left is not None:
            current = current.left
        return current
    
    def max_value(self):
        """
        Returns the maximum value in the BST.
        """
        return self._max_value_node(self.root).value
    
    def _max_value_node(self, node):
        """
        Helper method to find the node with the maximum value in the BST.
        """
        current = node
        while current.right is not None:
            current = current.right
        return current

    def inorder(self):
        """
        Returns the in-order traversal of the BST (left-root-right) as a list.
        """
        return self._inorder(self.root)

    def _inorder(self, node):
        """
        Helper method for in-order traversal.
        """
        if node is None:
            return []
        return (
            self._inorder(node.left)
            + [node.value]
            + self._inorder(node.right)
        )

    def preorder(self):
        """
        Returns the pre-order traversal of the BST (root-left-right) as a list.
        """
        return self._preorder(self.root)

    def _preorder(self, node):
        """
        Helper method for pre-order traversal.
        """
        if node is None:
            return []
        return (
            [node.value]
            + self._preorder(node.left)
            + self._preorder(node.right)
        )

    def postorder(self):
        """
        Returns the post-order traversal of the BST (left-right-root) as a list.
        """
        return self._postorder(self.root)

    def _postorder(self, node):
        """
        Helper method for post-order traversal.
        """
        if node is None:
            return []
        return (
            self._postorder(node.left)
            + self._postorder(node.right)
            + [node.value]
        )

# Example usage:
if __name__ == "__main__":
    path = "generation/binary_tree/bst_generation/"
    
    for mode in ["easy", "medium", "hard"]:
        with open(f"{path}bst_input_{mode}.txt", "w") as f:
            if mode == "easy":
                max_val = 100
                min_size = 5
                max_size = 10
            elif mode == "medium":
                max_val = 100
                min_size = 11
                max_size = 20
            else:
                max_val = 100
                min_size = 21
                max_size = 30
                
            for k in range(30):
                f.write(f"Tree {k}\n")
                size = random.randint(min_size, max_size)
                bst = BinarySearchTree()
                values = random.choice(max_val, size, replace=False)   
                print(values)
                tree = BinarySearchTree()
                for v in values:
                    tree.insert(v)
                traverse_tree(tree.root, f)
                