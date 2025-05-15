import random


class BPTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.children = []  # Only used for internal nodes

class BPTree:
    def __init__(self, order):
        self.order = order
        self.root = BPTreeNode(leaf=True)

    def _insert_into_leaf(self, leaf, key):
        leaf.keys.append(key)
        leaf.keys.sort()

    def _split_leaf(self, leaf):
        mid = len(leaf.keys) // 2
        new_leaf = BPTreeNode(leaf=True)
        new_leaf.keys = leaf.keys[mid:]
        leaf.keys = leaf.keys[:mid]
        return new_leaf.keys[0], new_leaf

    def _split_internal(self, node):
        mid = len(node.keys) // 2
        new_internal = BPTreeNode(leaf=False)
        new_internal.keys = node.keys[mid+1:]
        new_internal.children = node.children[mid+1:]
        up_key = node.keys[mid]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid+1]
        return up_key, new_internal

    def _insert(self, node, key):
        if node.leaf:
            self._insert_into_leaf(node, key)
            if len(node.keys) < self.order:
                return None, None
            else:
                return self._split_leaf(node)
        else:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            new_key, new_child = self._insert(node.children[i], key)
            if new_key is None:
                return None, None
            else:
                node.keys.insert(i, new_key)
                node.children.insert(i+1, new_child)
                if len(node.keys) < self.order:
                    return None, None
                else:
                    return self._split_internal(node)

    def insert(self, key):
        new_key, new_child = self._insert(self.root, key)
        if new_key is not None:
            new_root = BPTreeNode(leaf=False)
            new_root.keys = [new_key]
            new_root.children = [self.root, new_child]
            self.root = new_root

    def delete(self, key):
        # A simple deletion: traverse to the appropriate leaf and remove the key.
        node = self.root
        while not node.leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        if key in node.keys:
            node.keys.remove(key)
        # (Note: For simplicity, this version does not rebalance after deletion.)

    def get_preorder_traversal(self):
        """Return a list of nodes' keys in pre-order traversal."""
        result = []
        def dfs(node):
            result.append(node.keys)
            if not node.leaf:
                for child in node.children:
                    dfs(child)
        dfs(self.root)
        return result


for mode in ["easy", "medium", "hard"]:
    # Set order and number of operations range based on difficulty.
    if mode == "easy":
        order = 4
        n_range = (5, 10)
    elif mode == "medium":
        order = 6
        n_range = (11, 20)
    else:
        order = 8
        n_range = (21, 30)

    with open(f"compound_{mode}.txt", "w") as f:
        # Write a header indicating the tree order.
        for i in range(30):
            f.write(f"BPlusTree {i} (Order: {order})\n")
            n = random.randint(*n_range)
            tree = BPTree(order)
            keys_inserted = []
            for _ in range(n):
                op_probability = random.random()

                # With 30% chance, perform a deletion if keys exist.
                if op_probability < 0.3 and keys_inserted:
                    key = random.choice(keys_inserted)
                    tree.delete(key)
                    keys_inserted.remove(key)
                    f.write(f"delete {key}\n")
                else:
                    key = random.randint(0, 100)
                    tree.insert(key)
                    keys_inserted.append(key)
                    f.write(f"insert {key}\n")
            # Write the final state as a pre-order traversal (list of nodes' keys).
            final_preorder = tree.get_preorder_traversal()
            f.write(str(final_preorder) + "\n")

"""
if __name__ == "__main__":
    # Example usage
    bptree = BPTree(order=4)

    bptree.insert(2)
    print(bptree.get_preorder_traversal())
    bptree.insert(5)
    print(bptree.get_preorder_traversal())
    bptree.insert(50)
    print(bptree.get_preorder_traversal())
    bptree.insert(37)
    print(bptree.get_preorder_traversal())
    bptree.delete(50)
    print(bptree.get_preorder_traversal())
"""