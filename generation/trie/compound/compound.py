import random
import string

class TrieNode:
    def __init__(self, char=""):
        self.char = char
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode("")  # Root holds an empty string

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode(ch)
            node = node.children[ch]
        node.is_end = True

    def delete(self, word):
        def _delete(node, word, index):
            if index == len(word):
                if not node.is_end:
                    return False
                node.is_end = False
                return len(node.children) == 0
            ch = word[index]
            if ch not in node.children:
                return False
            should_delete = _delete(node.children[ch], word, index + 1)
            if should_delete:
                del node.children[ch]
                return not node.is_end and len(node.children) == 0
            return False

        _delete(self.root, word, 0)

    def pre_order_traversal(self):
        result = []

        def _dfs(node):
            result.append(node.char)
            for ch in sorted(node.children.keys()):
                _dfs(node.children[ch])

        _dfs(self.root)
        return result


# ----- Word Generation Function -----
def generate_random_word(target_length, existing_words):
    # If there are no words, generate a completely random word.
    if not existing_words:
        return ''.join(random.choices(string.ascii_lowercase, k=target_length))
    
    # Choose a random existing word.
    base_word = random.choice(list(existing_words))
    # Pick a random prefix length between 1 and target_length.
    prefix_length = random.randint(0, target_length)
    prefix = base_word if len(base_word) < prefix_length else base_word[:prefix_length]
    # Append random letters to reach the target length.
    remaining = target_length - len(prefix)
    if remaining > 0:
        suffix = ''.join(random.choices(string.ascii_lowercase, k=remaining))
        new_word = prefix + suffix
    else:
        new_word = prefix[:target_length]
    return new_word

# ----- Main Compound Input Generation -----
modes = ["easy", "medium", "hard"]
target_length_ranges = {
    "easy": (8, 12),    # Around 10 characters
    "medium": (18, 22), # Around 20 characters
    "hard": (28, 32)    # Around 30 characters
}

for mode in modes:
    low, high = target_length_ranges[mode]
    with open(f"compound_{mode}.txt", "w") as f:
        # Generate 30 test cases per mode.
        for i in range(30):
            f.write(f"TrieTree {i}\n")
            # Determine the number of operations based on difficulty.
            if mode == "easy":
                n = random.randint(5, 10)
            elif mode == "medium":
                n = random.randint(11, 20)
            else:
                n = random.randint(21, 30)
            
            # Create an empty trie.
            trie = Trie()
            # Also track the set of inserted words for word generation.
            current_words = set()
            
            for _ in range(n):
                op_probability = random.random()

                # With 30% chance, delete an existing word if available.
                if op_probability < 0.3 and current_words:
                    word = random.choice(list(current_words))
                    current_words.remove(word)
                    trie.delete(word)
                    f.write(f"delete {word}\n")
                else:
                    target_length = random.randint(low, high)
                    new_word = generate_random_word(target_length, current_words)
                    current_words.add(new_word)
                    trie.insert(new_word)
                    f.write(f"insert {new_word}\n")
            # Final state is the pre-order traversal of the trie.
            final_state = trie.pre_order_traversal()
            f.write(str(final_state) + "\n")


"""
if __name__ == "__main__":
    # Example usage
    trie = Trie()
    trie.insert("yvhjeofl")
    print(trie.pre_order_traversal())
    trie.insert("yvhjeofq")
    print(trie.pre_order_traversal())
    trie.delete("yvhjeofq")
    print(trie.pre_order_traversal())
    trie.insert("yvhjeycoudf")
    print(trie.pre_order_traversal())
    trie.insert("yvkxxqwqkm")
    print(trie.pre_order_traversal())
    trie.insert("yvhjeycoud")
    print(trie.pre_order_traversal())
    trie.delete("yvkxxqwqkm")
    print(trie.pre_order_traversal())
"""