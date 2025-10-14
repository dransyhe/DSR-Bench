import random

class MinHeap:
    def __init__(self):
        self.data = []

    def insert(self, value):
        self.data.append(value)
        self._sift_up(len(self.data) - 1)

    def delete(self):
        if not self.data:
            return None
        min_val = self.data[0]
        last = self.data.pop()
        if self.data:
            self.data[0] = last
            self._sift_down(0)
        return min_val

    def _sift_up(self, idx):
        while idx > 0:
            parent = (idx - 1) // 2
            if self.data[idx] < self.data[parent]:
                self.data[idx], self.data[parent] = self.data[parent], self.data[idx]
                idx = parent
            else:
                break

    def _sift_down(self, idx):
        n = len(self.data)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx

            if left < n and self.data[left] < self.data[smallest]:
                smallest = left
            # Tie-breaking: prefer left child when equal
            elif left < n and self.data[left] == self.data[smallest]:
                smallest = left

            if right < n and self.data[right] < self.data[smallest]:
                smallest = right

            if smallest != idx:
                self.data[idx], self.data[smallest] = self.data[smallest], self.data[idx]
                idx = smallest
            else:
                break

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "[" + ", ".join(map(str, self.data)) + "]"

# Main logic
for mode in ["easy", "medium", "hard"]:
    with open(f"compound_{mode}.txt", "w") as f:
        for i in range(30):
            if mode == "easy":
                n = random.randint(5, 10)
            elif mode == "medium":
                n = random.randint(11, 20)
            else:
                n = random.randint(21, 30)

            f.write(f"Heap {i}\n")

            heap = MinHeap()

            for _ in range(n):
                p = random.random()
                if p < 0.3:
                    operation_type = "delete"
                else:
                    operation_type = "insert"

                if operation_type == "insert" or len(heap) == 0:
                    value = random.randint(0, 100)
                    heap.insert(value)
                    f.write(f"insert {value}\n")
                elif operation_type == "delete":
                    heap.delete()
                    f.write("delete\n")

            f.write(str(heap) + "\n")
