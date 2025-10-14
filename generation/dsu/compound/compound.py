import random
import os


class DSU:
    def __init__(self, elements):
        # elements: list of unique values
        self.elements = list(elements)
        # map value -> internal index
        self.value_to_index = {v: i for i, v in enumerate(self.elements)}
        n = len(self.elements)
        self.parent = list(range(n))
        self.rank = [0] * n

    def _find_idx(self, idx):
        if self.parent[idx] != idx:
            self.parent[idx] = self._find_idx(self.parent[idx])
        return self.parent[idx]

    def find(self, x):
        """
        Given element x, return the root element value of x's set.
        """
        idx = self.value_to_index[x]
        root_idx = self._find_idx(idx)
        return self.elements[root_idx]

    def union(self, x, y):
        """
        Merge the sets containing elements x and y.
        x, y are actual element values.
        """
        idx_x = self.value_to_index[x]
        idx_y = self.value_to_index[y]
        ra = self._find_idx(idx_x)
        rb = self._find_idx(idx_y)
        if ra == rb:
            return
        # union by rank
        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1


def generate_dsu_instances(filename, mode):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        for _ in range(30):
            # 1) pick raw_len and max_unions by mode
            if mode == "easy":
                raw_len, max_unions = random.randint(10, 19), 10
            elif mode == "medium":
                raw_len, max_unions = random.randint(20, 39), 20
            else:  # hard
                raw_len, max_unions = random.randint(40, 59), 30

            # 2) generate raw_items with no duplicates
            raw_items = random.sample(range(0, 101), raw_len)
            f.write(f"{raw_items}\n")

            # 3) initialize DSU on element values
            dsu = DSU(raw_items)

            # 4) random union operations by values
            num_ops = random.randint(raw_len // 2, max_unions)
            for _op in range(num_ops):
                # pick two random elements
                a, b = random.choice(raw_items), random.choice(raw_items)
                f.write(f"union({a}, {b})\n")
                dsu.union(a, b)

            # 5) final state: find for each element value
            roots = [dsu.find(val) for val in raw_items]
            f.write(f"{roots}\n\n")


OUTPUT_DIR = "generation/dsu/compound"
for mode in ["easy", "medium", "hard"]:
    path = os.path.join(OUTPUT_DIR, f"compound_{mode}.txt")
    generate_dsu_instances(path, mode)
