#!/usr/bin/env python3
import os
import random
from collections import deque

# ── CONFIG ───────────────────────────────────────────────────────────────────────
module_dir = "./natural/queue/"
os.makedirs(module_dir, exist_ok=True)

mode = "hard"  # or "medium", "hard"
NUM_INSTANCES = 30
if mode == "easy":
    MIN_OPS, MAX_OPS = 5, 10
elif mode == "medium":
    MIN_OPS, MAX_OPS = 11, 20
else:
    MIN_OPS, MAX_OPS = 21, 30

natural_path = os.path.join(module_dir, f"natural-{mode}.txt")

# pools of names
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

def random_name(active):
    """Generate a new unique 'First Last' name not already in active."""
    while True:
        fn = random.choice(first_names)
        ln = random.choice(surnames)
        name = f"{fn} {ln}"
        if name not in active:
            return name

# ── GENERATE & WRITE ALL INSTANCES ───────────────────────────────────────────────
with open(natural_path, "w") as f:
    for _ in range(NUM_INSTANCES):
        active = set()    # who’s currently in the queue
        queue = deque()

        # generate a random sequence of operations
        num_ops = random.randint(MIN_OPS, MAX_OPS)
        for _ in range(num_ops):
            # enqueue if empty or 70% chance
            if not queue or random.random() < 0.7:
                name = random_name(active)
                active.add(name)
                queue.append(name)
                f.write(f"enqueue {name}\n")
            else:
                name = queue.popleft()
                active.remove(name)
                f.write(f"dequeue {name}\n")

        # blank line to separate ops from answer
        # final queue contents
        f.write(f"{list(queue)}\n")
