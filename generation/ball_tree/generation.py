import math
import numpy.random as random

class BallTree:
    class Node:
        __slots__ = ("center", "radius", "points", "left", "right")
        def __init__(self, center, radius, points=None, left=None, right=None):
            # center:  [x, y] of this ball
            # radius:  float, max distance from center to any point in this node
            # points:  list of points if leaf, else None
            # left/right: child Nodes
            self.center = center
            self.radius = radius
            self.points = points
            self.left = left
            self.right = right

    def __init__(self, points, leaf_size=10, distance_func=None):
        """
        :param points:      list of 2D points, each a [x, y] list
        :param leaf_size:   max #points in a leaf before stopping recursion
        :param distance_func: optional metric, defaults to Euclidean
        """
        self.leaf_size = leaf_size
        self.distance = distance_func or self._euclidean
        self.root = self._build(points)

    def _euclidean(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _build(self, pts):
        if not pts:
            return None

        # 1) Compute centroid and covering radius
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        center = [cx, cy]
        radius = max(self.distance(center, p) for p in pts)

        # 2) If small enough, make leaf
        if len(pts) <= self.leaf_size:
            return BallTree.Node(center, radius, points=pts)

        # 3) Choose two “pivots” by the 2‑step farthest heuristic
        p0 = pts[0]
        # farthest from p0
        B = max(pts, key=lambda p: self.distance(p0, p))
        # farthest from B
        C = max(pts, key=lambda p: self.distance(B, p))

        # 4) Partition on which pivot is closer
        left_pts, right_pts = [], []
        for p in pts:
            if self.distance(p, B) <= self.distance(p, C):
                left_pts.append(p)
            else:
                right_pts.append(p)

        # 5) Recurse
        left_node  = self._build(left_pts)
        right_node = self._build(right_pts)
        return BallTree.Node(center, radius, left=left_node, right=right_node)

    def radius_search(self, query, tau):
        """
        Return all points within distance <= tau of the query point.
        """
        result = []
        def _search(node):
            if node is None:
                return
            dcen = self.distance(query, node.center)
            # prune if the whole ball is too far
            if dcen - node.radius > tau:
                return
            if node.points is not None:
                # leaf: check individually
                for p in node.points:
                    if self.distance(query, p) <= tau:
                        result.append(p)
            else:
                # internal: recurse both children
                _search(node.left)
                _search(node.right)

        _search(self.root)
        return result
    
    def preorder(self):
        """
        Return a pre-order traversal of the tree.
        """
        result = []

        def _preorder(node):
            if node is None:
                return
            result.append(node.center)
            _preorder(node.left)
            _preorder(node.right)

        _preorder(self.root)
        return result

# Example usage
if __name__ == "__main__":

    path = "generation/ball_tree"
    
    for mode in ["easy"]: # "easy", "medium", "hard"
        all_points = []
        all_traversals = []
        with open(f"{path}/construction/bt_construction_{mode}.txt", "w") as f:
            if mode == "easy":
                M = 2
                min_size = 5
                max_size = 10
            elif mode == "medium":
                M = 3
                min_size = 15
                max_size = 20
            else:
                M = 5
                min_size = 21
                max_size = 30
                
            for k in range(30):
                size = max_size
                points = random.randint(0, 100, (size, 2)).tolist()
                tree = BallTree(points, leaf_size=M)
                traversal = [node for node in tree.preorder()]
                
                f.write(f"Tree {k}, M = {tree.leaf_size}\n")
                f.write(f"Points: {[list(pt) for pt in points]}\n")
                f.write(f"Traversal: {[list(pt) for pt in traversal]}\n")
                
                
    # pts = [
    #     [1,2], [3,4], [1,5],
    #     [6,1], [4,2], [2,2],
    #     [8,9], [9,9], [8,8]
    # ]
    # tree = BallTree(pts, leaf_size=2)
    
    # print("Pre-order traversal of the tree:")
    # print(tree.preorder())

    # query = [2,3]
    # tau = 2.5
    # neighbors = tree.radius_search(query, tau)
    # print(f"Points within {tau} of {query}: {neighbors}")
