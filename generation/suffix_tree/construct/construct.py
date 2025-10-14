import random
import string


class SuffixTreeNode:
    def __init__(self):
        self.children = {}

class SuffixTree:
    def __init__(self, text):
        # Append a terminal symbol if it isn't already there.
        if text[-1] != '$':
            text += '$'
        self.root = SuffixTreeNode()
        self.text = text
        self._build()

    def _build(self):
        for i in range(len(self.text)):
            suffix = self.text[i:]
            self._insert_suffix(suffix)

    def _insert_suffix(self, suffix):
        node = self.root
        while suffix:
            first = suffix[0]
            if first in node.children:
                label, child = node.children[first]
                j = 0
                while j < len(label) and j < len(suffix) and label[j] == suffix[j]:
                    j += 1
                if j == len(label):
                    # Follow the matched edge and continue deeper
                    node = child
                    suffix = suffix[j:]
                else:
                    # Split required
                    existing_label, existing_child = label, child
                    mid_node = SuffixTreeNode()

                    # Add the remaining part of the existing label
                    mid_node.children[existing_label[j]] = (existing_label[j:], existing_child)

                    if j < len(suffix):
                        # Add the remaining part of the new suffix
                        mid_node.children[suffix[j]] = (suffix[j:], SuffixTreeNode())

                    # Replace the original edge with the new split
                    node.children[first] = (label[:j], mid_node)
                    return
            else:
                # No match at all, insert new leaf
                node.children[first] = (suffix, SuffixTreeNode())
                return


    def pre_order_traversal(self):
        result = []

        def dfs(node):
            for key in sorted(node.children):
                label, child = node.children[key]
                result.append(label)
                dfs(child)

        dfs(self.root)
        return result



# Difficulty settings with word length ranges.
modes = ["easy", "medium", "hard"]
length_ranges = {
    "easy": (5, 10),    
    "medium": (11, 20), 
    "hard": (21, 30)    
}

for mode in modes:
    with open(f"construct_{mode}.txt", "w") as f:
        for i in range(30):
            f.write(f"SuffixTree {i}\n")
            
            # Generate one random word of length based on difficulty.
            low, high = length_ranges[mode]
            length = random.randint(low, high)
            word = ''.join(random.choices(string.ascii_lowercase, k=length))
            f.write(f"{word}$\n")
            
            # Build the suffix trie and write its pre-order traversal.
            tree = SuffixTree(word)
            traversal = tree.pre_order_traversal()
            f.write(str(traversal) + "\n")


