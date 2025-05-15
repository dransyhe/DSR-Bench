import numpy as np
import numpy.random as random
from generation.binary_tree.tree_utils import traverse_tree
from generation.kd_tree.gen_data import gen_circle, gen_moons, gen_blobs

random.seed(0)

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
        
class KDTree:
    def __init__(self, points = []):
        self.root = self.build(points, depth=0)
        
    def build(self, points, depth):
        if len(points) == 0:
            return None

        k = len(points[0])  # number of dimensions
        axis = depth % k
        
        # Sort points by the current axis and select the median
        sorted_indices = np.argsort(points[:, axis])
        points = points[sorted_indices]
        median_index = len(points) // 2
        
        # Create node and construct subtrees
        node = Node(points[median_index])
        node.left = self.build(points[:median_index], depth + 1)
        node.right = self.build(points[median_index + 1:], depth + 1)
        
        return node
    
    def insert(self, point):
        self.root = self._insert(self.root, point, depth=0)
        
    def _insert(self, node, point, depth):
        if node is None:
            return Node(point)

        k = len(point)
        axis = depth % k
        
        # Compare the point with the current node and decide to go left or right
        if point[axis] < node.value[axis]:
            node.left = self._insert(node.left, point, depth + 1)
        else:
            node.right = self._insert(node.right, point, depth + 1)
        
        return node
    
    def delete(self, point):
        self.root = self._delete(self.root, point, depth=0)
        
    def _delete(self, node, point, depth):
        if node is None:
            return None

        k = len(point)
        
        # Compare the point with the current node and decide to go left or right
        if point == node.value:
            # Node to be deleted found
            if node.right is not None:
                # Find the minimum value in the right subtree
                min_value = self._find_min(node.right, depth)
                node.value = min_value
                node.right = self._delete(node.right, min_value, depth + 1)
            else:
                return node.left
            
    def traverse(self):
        return self._traverse(self.root)
    
    def _traverse(self, node):
        if node is None:
            return []
        return [node.value] + self._traverse(node.left) + self._traverse(node.right)
    
    def __eq__(self, other):
        if not isinstance(other, KDTree):
            return False
        return np.array_equal(self.traverse(), other.traverse())

if __name__ == "__main__":
    
    dim = 2
    dist = "blob"
    
    for mode in ["easy", "medium", "hard"]: # , "medium", "hard"
        all_points = []
        all_traversals = []
        with open(f"generation/kd_tree/construct_{dist}/construct_{mode}.txt", "w") as f:
            if mode == "easy":
                dimension = dim
                min_size = 5
                max_size = 10
            elif mode == "medium":
                dimension = dim
                min_size = 15
                max_size = 20
            else:
                dimension = dim
                min_size = 21
                max_size = 30
                
            for k in range(30):
                f.write(f"Tree {k}\n")
                size = random.randint(min_size, max_size)
                if dist == "circle":
                    points = gen_circle(size, k)
                elif dist == "moon":
                    points = gen_moons(size, k)
                elif dist == "blob":
                    points = gen_blobs(size, k)
                else:
                    points = random.randint(0, 100, (size, dimension))

                tree = KDTree(points)
    
                f.write(f"Points: {[list(pt) for pt in points]}\n")
                f.write(f"Traversal: {[list(pt) for pt in KDTree.traverse(tree)]}\n")
    
                