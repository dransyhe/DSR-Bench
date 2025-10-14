import random
import string
from collections import deque


class DAWGNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.signature = None  # Used during minimization.


class DAWG:
    def __init__(self):
        self.root = DAWGNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = DAWGNode()
            node = node.children[ch]
        node.is_end = True

    def delete(self, word):
        def _delete(node, word, depth):
            if depth == len(word):
                if not node.is_end:
                    return False
                node.is_end = False
                return len(node.children) == 0
            ch = word[depth]
            if ch not in node.children:
                return False
            should_delete = _delete(node.children[ch], word, depth + 1)
            if should_delete:
                del node.children[ch]
                return (not node.is_end) and (len(node.children) == 0)
            return False
        _delete(self.root, word, 0)

    def minimize(self):
        registry = {}
        def _minimize(node):
            new_children = {}
            for letter, child in node.children.items():
                new_children[letter] = _minimize(child)
            node.children = new_children
            sig_children = tuple(sorted((letter, child.signature) for letter, child in node.children.items()))
            signature = (node.is_end, sig_children)
            if signature in registry:
                return registry[signature]
            else:
                node.signature = signature
                registry[signature] = node
                return node
        self.root = _minimize(self.root)

    def get_bfs_traversal(self):
        """
        Returns a list of lists [prefix, flag] in breadth-first order,
        where flag is 'T' if is_end else 'F'.
        """
        result = []
        queue = deque([(self.root, "")])
        visited = set()
        while queue:
            node, prefix = queue.popleft()
            if id(node) in visited:
                continue
            visited.add(id(node))
            # Record prefix and 'T'/'F' flag
            flag = 'T' if node.is_end else 'F'
            result.append([prefix, flag])
            for ch in sorted(node.children.keys()):
                queue.append((node.children[ch], prefix + ch))
        return result


modes = ["easy", "medium", "hard"]
word_length_ranges = {
    "easy": (3, 6),
    "medium": (5, 10),
    "hard": (8, 15)
}

for mode in modes:
    low, high = word_length_ranges[mode]
    with open(f"compound_{mode}.txt", "w") as f:
        for i in range(30):
            f.write(f"DAWG {i}\n")
            n = random.randint(5, 10) if mode == "easy" else random.randint(11, 20) if mode == "medium" else random.randint(21, 30)

            dawg = DAWG()
            current_words = set()

            for _ in range(n):
                op_prob = random.random()
                if op_prob < 0.3 and current_words:
                    word = random.choice(list(current_words))
                    dawg.delete(word)
                    current_words.remove(word)
                    f.write(f"delete {word}\n")
                else:
                    # Increase head-sharing: 50% chance to reuse a prefix of an existing word
                    if current_words and random.random() < 0.5:
                        existing = random.choice(list(current_words))
                        prefix_len = random.randint(1, len(existing))
                        prefix = existing[:prefix_len]
                        target_len = random.randint(low, high)
                        suffix_len = max(target_len - len(prefix), 1)
                        suffix = ''.join(random.choices(string.ascii_lowercase, k=suffix_len))
                        word = prefix + suffix
                    else:
                        length = random.randint(low, high)
                        word = ''.join(random.choices(string.ascii_lowercase, k=length))
                    dawg.insert(word)
                    current_words.add(word)
                    f.write(f"insert {word}\n")

            dawg.minimize()
            final_state = dawg.get_bfs_traversal()
            f.write(str(final_state) + "\n")

"""
if __name__ == "__main__":
    # Example usage
    dawg = DAWG()
    dawg.insert("dzso")
    print(dawg.get_bfs_traversal())
    dawg.insert("gyr")
    print(dawg.get_bfs_traversal())
    dawg.insert("gqqvvl")
    print(dawg.get_bfs_traversal())
    dawg.delete("gqqvvl")
    print(dawg.get_bfs_traversal())
    dawg.insert("dar")
    print(dawg.get_bfs_traversal())
    dawg.minimize()
    print(dawg.get_bfs_traversal())
"""