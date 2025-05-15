import random
import os
from collections import deque

class MaxFibonacciHeap:
    """
    A *very* simplified Fibonacci‑heap stub that actually *records* a forest of
    heap‑ordered trees so that we can do a pre‑order traversal at the end.
    (No real consolidation or cascading cuts—just enough structure for drawing.)
    """
    class Node:
        def __init__(self, value, priority):
            self.value    = value
            self.key      = priority
            self.parent   = None
            self.children = []      # actual child pointers

    def __init__(self):
        self.roots = []           # list of current root nodes

    def insert(self, value, priority):
        node = MaxFibonacciHeap.Node(value, priority)
        self.roots.append(node)
        return node

    def extract_max(self):
        if not self.roots:
            raise IndexError("extract_max from empty heap")
        node = max(self.roots, key=lambda n: (n.key, n.value))
        self.roots.remove(node)
        for c in node.children:
            c.parent = None
            self.roots.append(c)
        return node

    def increase_key(self, node, new_priority):
        if new_priority < node.key:
            raise ValueError("new priority must be ≥ old priority")
        node.key = new_priority

    def decrease_key(self, node, new_priority):
        if new_priority > node.key:
            raise ValueError("new priority must be ≤ old priority")
        node.key = new_priority

    def is_empty(self):
        return not self.roots

    def preorder(self):
        result = []
        def dfs(n):
            result.append((n.value, n.key))
            for c in sorted(n.children, key=lambda x: (-x.key, -x.value)):
                dfs(c)
        for root in sorted(self.roots, key=lambda x: (-x.key, -x.value)):
            dfs(root)
        return result

    def level_order(self):
        """
        Return a list of (value, priority) by visiting:
           1) all roots, then
           2) all their children, then
           3) all grandchildren, …
        Within each level, siblings are visited in descending (priority, value) order.
        """
        result = []
        queue = deque(
            sorted(self.roots, key=lambda n: (-n.key, -n.value))
        )
        while queue:
            node = queue.popleft()
            result.append((node.value, node.key))
            # enqueue this node’s children—again in descending (key,value)
            for c in sorted(node.children, key=lambda x: (-x.key, -x.value)):
                queue.append(c)
        return result

# ————————————————
# Test‑generator with no‑duplicate random values
# ————————————————

base_path = "generation/priority_queue/compound"
os.makedirs(base_path, exist_ok=True)

for mode in ["easy", "medium", "hard"]:
    with open(f"{base_path}/compound_{mode}.txt", "w") as f:
        for i in range(30):
            if mode == "easy":
                num_ops = random.randint(5, 10)
            elif mode == "medium":
                num_ops = random.randint(11, 20)
            else:
                num_ops = random.randint(21, 30)

            f.write(f"PriorityQueue {i}\n")

            # Build a shuffled pool of unique values 0–100
            pool = list(range(101))
            random.shuffle(pool)

            pq = MaxFibonacciHeap()
            nodes = {}

            for _ in range(num_ops):
                if not pq.is_empty() and random.random() < 0.5:
                    op = random.choice(["delete", "raise_key", "decrease_key"])
                else:
                    op = "insert"

                if op == "insert":
                    # pop a unique random value
                    v = pool.pop()
                    p = random.randint(0, 100)
                    node = pq.insert(v, p)
                    nodes[v] = node
                    f.write(f"insert ({v}, {p})\n")

                elif op == "delete":
                    node = pq.extract_max()
                    del nodes[node.value]
                    f.write("delete\n")

                elif op == "raise_key":
                    v = random.choice(list(nodes))
                    old = nodes[v].key
                    new = min(100, old + random.randint(1, 50))
                    pq.increase_key(nodes[v], new)
                    f.write(f"raise_key ({v}, {new})\n")

                else:  # decrease_key
                    v = random.choice(list(nodes))
                    old = nodes[v].key
                    new = max(0, old - random.randint(1, 50))
                    pq.decrease_key(nodes[v], new)
                    f.write(f"decrease_key ({v}, {new})\n")

            order = pq.level_order()
            order = [list(pair) for pair in order]  
            f.write(str(order) + "\n")
