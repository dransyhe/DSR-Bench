class BKTree:
    class Node:
        def __init__(self, point):
            """
            Each node represents a 2D point stored as a Python list and has a dictionary of children.
            The dictionary keys are the integer distances from this point.
            """
            self.point = point  # A 2D point represented as a list, e.g., [x, y]
            self.children = {}  # Maps integer distances to child nodes

    def __init__(self, distance_func):
        """
        Initializes the BK Tree.
        :param distance_func: A function that takes two points and returns an integer distance.
        """
        self.distance_func = distance_func
        self.root = None

    def insert(self, point):
        """
        Inserts a new point (a 2D list) into the BK tree.
        """
        if self.root is None:
            self.root = BKTree.Node(point)
            return

        current = self.root
        while True:
            d = self.distance_func(point, current.point)
            # If the distance is 0, the point is identical to an existing one, so we skip insertion.
            if d == 0:
                return
            if d in current.children:
                current = current.children[d]
            else:
                current.children[d] = BKTree.Node(point)
                break

    def search(self, query_point, threshold):
        """
        Searches for all points in the BK tree that are within the given Manhattan distance threshold from query_point.
        Returns a list of tuples: (point, distance).
        """
        results = []

        def _search(node):
            d = self.distance_func(query_point, node.point)
            if d <= threshold:
                results.append((node.point, d))
            # Explore children nodes that could potentially contain points within the threshold.
            for child_distance, child in node.children.items():
                if d - threshold <= child_distance <= d + threshold:
                    _search(child)

        if self.root is not None:
            _search(self.root)
        return results

    def preorder(self):
        """
        Returns the preorder traversal of the BK tree as a list of points.
        Preorder traversal means visiting the current node first then all the children.
        """
        result = []

        def _preorder(node):
            if node is None:
                return
            result.append(node.point)
            for child in node.children.values():
                _preorder(child)

        if self.root is not None:
            _preorder(self.root)
        return result
    
    def visualize(self, node=None, indent=""):
        """
        Helper function to visualize the structure of the BK tree.
        :param node: The current node to visualize (defaults to the root).
        :param indent: The indentation string used for formatting the tree display.
        """
        if node is None:
            node = self.root
        if node is None:
            print(indent + "Empty tree")
            return

        # Print the current node's point.
        print(indent + f"{node.point}")
        for dist, child in node.children.items():
            # Print the edge distance to each child.
            print(indent + f"  [distance: {dist}]")
            # Recursively visualize child nodes with extra indentation.
            self.visualize(child, indent + "    ")

# Define a Manhattan distance function for 2D points represented as lists.
def manhattan_distance(point1, point2):
    """
    Compute the Manhattan (L1) distance between two 2D points represented as lists.
    :param point1: List [x1, y1]
    :param point2: List [x2, y2]
    :return: Integer distance |x1 - x2| + |y1 - y2|
    """
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

# Example usage:
if __name__ == "__main__":
    # Create a BK tree using the Manhattan distance metric.
    tree = BKTree(manhattan_distance)
    
    # Insert a few points (represented as lists) into the tree.
    points = [[1, 2], [3, 4], [1, 5], [6, 1], [4, 2], [2, 2]]
    for pt in points:
        tree.insert(pt)
    
    # Define a query point and a distance threshold.
    query = [2, 3]
    threshold = 3
    
    # Search for points within the threshold distance from the query point.
    matches = tree.search(query, threshold)
    
    print("Query point:", query)
    print("Points within a Manhattan distance of {}:".format(threshold))
    for match, dist in matches:
        print("  Point: {} - Distance: {}".format(match, dist))
    
    # Output the preorder traversal of the BK tree.
    preorder_points = tree.preorder()
    print("\nPreorder traversal of the BK tree:")
    print(preorder_points)
    
    print("\nVisualizing the BK tree:")
    tree.visualize()
