import numpy as np
from numpy import random

class KDHeap:
    def __init__(self):
        self.data = []

    def push(self, priority_vec, node):
        dist2 = self._squared_norm(priority_vec)
        self.data.append([dist2, priority_vec, node])
        self._sift_up(len(self.data) - 1)

    def pop(self):
        if not self.data:
            return None
        self._swap(0, len(self.data) - 1)
        dist2, priority_vec, node = self.data.pop()
        self._sift_down(0)
        return priority_vec, node

    def is_empty(self):
        return len(self.data) == 0
    
    def __len__(self):
        return len(self.data)
    
    def _squared_norm(self, vec):
        return sum(v * v for v in vec)

    def _sift_up(self, idx):
        parent = (idx - 1) // 2
        while idx > 0 and self.data[idx][0] < self.data[parent][0]:
            self._swap(idx, parent)
            idx = parent
            parent = (idx - 1) // 2

    def _sift_down(self, idx):
        n = len(self.data)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx
            if left < n and self.data[left][0] < self.data[smallest][0]:
                smallest = left
            if right < n and self.data[right][0] < self.data[smallest][0]:
                smallest = right
            if smallest == idx:
                break
            self._swap(idx, smallest)
            idx = smallest

    def _swap(self, i, j):
        self.data[i], self.data[j] = self.data[j], self.data[i]
        
    def __str__(self):
        return "[" + ", ".join(map(str, [node for _, _, node in self.data])) + "]"
    
        
k = 5
# Main logic
for mode in ["easy", "medium", "hard"]:
    with open(f"generation/kd_heap/compound_{k}d/compound_{mode}.txt", "w") as f:
        for i in range(30):
            if mode == "easy":
                n = random.randint(5, 10)
            elif mode == "medium":
                n = random.randint(11, 20)
            else:
                n = random.randint(21, 30)

            f.write(f"Heap {i}, Dimension: {k}\n")

            heap = KDHeap()

            for _ in range(n):
                p = random.random()
                if p < 0.3:
                    operation_type = "delete"
                else:
                    operation_type = "insert"

                if operation_type == "insert" or len(heap) == 0:
                    node = random.randint(0, 100)
                    priority = list(random.randint(0, 100, size=(k,)))
                    heap.push(priority, node)
                    f.write(f"insert ({node}, {priority})\n")
                elif operation_type == "delete":
                    heap.pop()
                    f.write("delete\n")

            f.write(str(heap) + "\n")
