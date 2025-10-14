import random

class Node:
    def __init__(self, key, level):
        self.key = key
        self.forward = [None] * (level + 1)

class SkipList:
    def __init__(self, max_level):
        self.max_level = max_level
        self.header = Node(-1, self.max_level)
        self.level = 0  # current maximum level in the skip list

    def random_level(self, probs=None):
        lvl = 0
        probabilities = []
        # Continue generating until the condition fails or max_level is reached.
        while True:
            if probs is None:
                p_val = random.random()
                probabilities.append(p_val)
            else:
                p_val = probs.pop(0)
            if p_val < 0.5 and lvl < self.max_level:
                lvl += 1
            else:
                break
        return lvl, probabilities

    def insert(self, key, probs=None, file_handle=None):
        update = [None] * (self.max_level + 1)
        current = self.header

        # Move down levels from the top to bottom, tracking the path
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current

        current = current.forward[0]

        # Only insert if the key is not already present
        if current is None or current.key != key:
            lvl, level_probs = self.random_level(probs=probs)

            # Record the level generation probabilities if a file handle is provided
            if file_handle is not None:
                file_handle.write("Level generation probabilities: " + 
                                  ", ".join(f"{p_val:.4f}" for p_val in level_probs) + "\n")

            if lvl > self.level:
                for i in range(self.level + 1, lvl + 1):
                    update[i] = self.header
                self.level = lvl

            new_node = Node(key, lvl)
            for i in range(lvl + 1):
                new_node.forward[i] = update[i].forward[i]
                update[i].forward[i] = new_node

    def delete(self, key):
        update = [None] * (self.max_level + 1)
        current = self.header

        # Find the node to be deleted and track the update path
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current

        current = current.forward[0]

        # If the key is found, remove it from each level
        if current and current.key == key:
            for i in range(self.level + 1):
                if update[i].forward[i] != current:
                    break
                update[i].forward[i] = current.forward[i]

            # Reduce the level of the skip list if necessary
            while self.level > 0 and self.header.forward[self.level] is None:
                self.level -= 1

    def delete_min(self):
        # Delete the smallest element (first element at level 0)
        if self.header.forward[0] is None:
            return None
        min_key = self.header.forward[0].key
        self.delete(min_key)
        return min_key

    def get_elements(self):
        # Return a list of all keys in the bottom level (sorted order)
        result = []
        node = self.header.forward[0]
        while node:
            result.append(node.key)
            node = node.forward[0]
        return result

    def get_levels(self):
        # Return a list of lists representing each level (from highest level to level 0)
        levels = []
        for i in range(self.level, -1, -1):
            level_list = []
            node = self.header.forward[i]
            while node:
                level_list.append(node.key)
                node = node.forward[i]
            levels.append(level_list)
        return levels


# Generate random examples for skip list operations based on difficulty mode
for mode in ["easy", "medium", "hard"]:
    # Set a reasonable max_level based on difficulty
    if mode == "easy":
        max_level = 3
    elif mode == "medium":
        max_level = 5
    else:  # hard
        max_level = 7

    with open(f"compound_{mode}.txt", "w") as f:
        # Generate 30 test cases per mode
        for i in range(30):
            f.write(f"SkipList {i} (Max Level: {max_level})\n")

            if mode == "easy":
                n = random.randint(5, 10)
            elif mode == "medium":
                n = random.randint(11, 20)
            else:
                n = random.randint(21, 30)
            
            # Start with an empty skip list with the specified max_level
            skiplist = SkipList(max_level)
            values = []
            
            # Perform a sequence of random operations
            for _ in range(n):
                op_probability = random.random()              
                if op_probability < 0.3:
                    operation_type = "delete"
                else:
                    operation_type = "insert"
                
                # If the skip list is empty, force an insertion
                if operation_type == "insert" or not skiplist.get_elements():
                    value = random.randint(0, 100)
                    f.write(f"insert {value}\n")
                    values.append(value)
                    skiplist.insert(value, file_handle=f)
                elif operation_type == "delete":
                    deleted_value = random.choice(values) 
                    values.remove(deleted_value)
                    skiplist.delete(deleted_value)
                    f.write(f"delete {deleted_value}\n")
            
            # Write the final state of the skip list as a list of lists (one list per level)
            final_levels = skiplist.get_levels()
            f.write(str(final_levels) + "\n")

"""
if __name__ == "__main__":
    # Example usage
    skiplist = SkipList(max_level=3)
    skiplist.insert(43, probs=[0.1412, 0.6574])
    print(skiplist.get_levels())
    skiplist.insert(3, probs=[0.9823])
    print(skiplist.get_levels())
    skiplist.delete(3)
    print(skiplist.get_levels())
    skiplist.insert(89, probs=[0.4328, 0.7636])
    print(skiplist.get_levels())
    skiplist.delete(89)
    print(skiplist.get_levels())
"""
