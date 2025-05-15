#!/usr/bin/env python3
import random
import os

# --- helper to serialize the post-order list of (name, time) ---
def tuple_list_to_str(lst):
    if not lst:
        return "[]\n"
    inner = ", ".join(f"('{n}', '{t}')" for n, t in lst)
    return f"[{inner}]\n"

# --- name pools (you can expand these) ---
first_names = [
    "Liam", "Noah", "Oliver", "Elijah", "Lucas", "Mason", "Logan", "Ethan",
    "Emma", "Ava", "Sophia", "Isabella", "Mia", "Amelia", "Harper", "Evelyn",
    "Aiden", "Caden", "Grayson", "Jackson", "Aria", "Layla", "Chloe", "Ella",
    "Haruto", "Yuki", "Sakura", "Hiroshi", "Mei", "Ling", "Fatima", "Aisha",
    "Hassan", "Ali", "Carlos", "Maria", "Sofia", "Mateo", "Diego", "Valentina"
]
surnames = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Clark", "Lewis", "Walker", "Hall",
    "Young", "Allen", "Nguyen", "Chen", "Patel", "Kumar", "Singh", "Ali",
    "Hassan", "Wang", "Yamamoto", "Kobayashi", "Fernandez", "Sanchez"
]

# --- BST node and operations ---
class Node:
    def __init__(self, name, time):
        self.name = name
        self.time = time
        self.left = None
        self.right = None

def cmp_key(t1, n1, t2, n2):
    """Compare (time, name) lex order."""
    if t1 < t2: return -1
    if t1 > t2: return  1
    if n1 < n2: return -1
    if n1 > n2: return  1
    return 0

def bst_insert(root, name, time):
    if root is None:
        return Node(name, time)
    c = cmp_key(time, name, root.time, root.name)
    if c < 0:
        root.left = bst_insert(root.left, name, time)
    else:
        root.right = bst_insert(root.right, name, time)
    return root

def bst_delete(root, name, time):
    if root is None:
        return None
    c = cmp_key(time, name, root.time, root.name)
    if c < 0:
        root.left = bst_delete(root.left, name, time)
    elif c > 0:
        root.right = bst_delete(root.right, name, time)
    else:
        # found node
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        # two children: replace with successor
        succ = root.right
        while succ.left:
            succ = succ.left
        root.name, root.time = succ.name, succ.time
        root.right = bst_delete(root.right, succ.name, succ.time)
    return root

def pre_order(root, out):
    if not root:
        return
    out.append((root.name, root.time))
    pre_order(root.left, out)
    pre_order(root.right, out)

# --- time generator ---
def random_time():
    h = random.randint(8, 16)          # hours 08–16
    m = random.randint(0, 59)          # minutes 00–59
    return f"{h:02d}:{m:02d}"

# --- main generation ---
def main():
    NUM_INSTANCES = 30
    mode = "hard"
    if mode == "easy":
        MIN_OPS, MAX_OPS = 5, 10
    elif mode == "medium":
        MIN_OPS, MAX_OPS = 11, 20
    else:
        MIN_OPS, MAX_OPS = 21, 30

    out_path = f"./natural/bst/natural-{mode}.txt"
    with open(out_path, "w") as f:
        for inst in range(NUM_INSTANCES):
            # for delete lookups
            active = {}  # name → time
            root = None

            num_ops = random.randint(MIN_OPS, MAX_OPS)
            for _ in range(num_ops):
                # if empty tree, force insert
                do_insert = not active or random.random() < 0.7

                if do_insert:
                    # pick a new random name
                    fn = random.choice(first_names)
                    ln = random.choice(surnames)
                    name = f"{fn} {ln}"

                    # ensure uniqueness
                    while name in active:
                        fn = random.choice(first_names)
                        ln = random.choice(surnames)
                        name = f"{fn} {ln}"

                    time = random_time()
                    active[name] = time
                    root = bst_insert(root, name, time)
                    f.write(f"insert {name} {time}\n")
                else:
                    # delete a random existing patient
                    name = random.choice(list(active.keys()))
                    time = active.pop(name)
                    root = bst_delete(root, name, time)
                    f.write(f"delete {name}\n")

            # collect and write pre-order traversal
            po = []
            pre_order(root, po)
            f.write(tuple_list_to_str(po))

            # blank line between instances
            f.write("\n")

    print(f"Generated → {out_path}")

if __name__ == "__main__":
    main()
