import random

def custom_hash(item, salt, m):
    """
    Custom hash function:
    1. Convert the input 'item' to a string.
    2. Initialize the hash value h to 0.
    3. For each character in the string, update h as: h = h * 131 + ord(character)
    4. Add the salt value to h.
    5. Return h modulo m.
    """
    # print(f"We hash item: {item} with salt {salt} and size {m}.")
    s = str(item)
    h = 0
    for char in s:
        h = h * 131 + ord(char)
    # print(f"Startin from h=0, for each char c in str({item}), we compute h = h * 131 + ord(c), giving us the intermediate hash value: {h}.")
    h = h + salt
    # print(f"Add the salt value {salt} to h, giving us {h}.")
    # print(f"The final hash value is h modulo m: {h % m}.")
    # print(f"We increment 1 to index {h % m} in the bloom filter.")
    return h % m


class CountingBloomFilter:
    def __init__(self, m, k):
        self.m = m        # Size of the count array.
        self.k = k        # Number of hash functions.
        self.count_array = [0] * m  # Counters for each position.

    def _hashes(self, item):
        """Generate k hash values for the item."""
        hashes = []
        for i in range(self.k):
            h = abs(custom_hash(item, i, self.m))
            hashes.append(h)
        return hashes

    def insert(self, item):
        """Insert an item into the counting Bloom filter by incrementing counters."""
        for h in self._hashes(item):
            self.count_array[h] += 1

    def delete(self, item):
        """Delete an item by decrementing the corresponding counters (ensuring no negative values)."""
        for h in self._hashes(item):
            if self.count_array[h] > 0:
                self.count_array[h] -= 1

    def query(self, item):
        """
        Check membership: The item is considered present if all corresponding counters are greater than 0.
        (This method is provided for completeness, although only insert and delete operations are used.)
        """
        return all(self.count_array[h] > 0 for h in self._hashes(item))

    def get_state(self):
        """Return the current state of the counting Bloom filter (the count array)."""
        return self.count_array


# Define difficulty levels and corresponding parameters.
modes = ["easy", "medium", "hard"]
# Parameters: (m, k)
parameters = {
    "easy": (20, 3),
    "medium": (50, 4),
    "hard": (100, 5)
}

for mode in modes:
    m, k = parameters[mode]
    with open(f"compound_{mode}.txt", "w") as f:
        # Write a header indicating the filter parameters.
        for i in range(30):
            f.write(f"CountingBloomFilter {i} (m: {m}, k: {k})\n")
            # Determine number of operations based on mode.
            if mode == "easy":
                n = random.randint(5, 10)
            elif mode == "medium":
                n = random.randint(11, 20)
            else:
                n = random.randint(21, 30)
            cbf = CountingBloomFilter(m, k)
            # Keep track of inserted items to make deletion valid.
            inserted_items = []
            for _ in range(n):
                op_probability = random.random()
                if op_probability < 0.7:
                    item = random.randint(0, 100)
                    cbf.insert(item)
                    inserted_items.append(item)
                    f.write(f"insert {item}\n")
                else:
                    if inserted_items:
                        item = random.choice(inserted_items)
                        cbf.delete(item)
                        inserted_items.remove(item)
                        f.write(f"delete {item}\n")
                    else:
                        item = random.randint(0, 100)
                        cbf.insert(item)
                        inserted_items.append(item)
                        f.write(f"insert {item}\n")
            final_state = cbf.get_state()
            f.write(str(final_state) + "\n")


"""
if __name__ == "__main__":
    # Example usage
    m = 20  # Size of the count array
    k = 3   # Number of hash functions
    cbf = CountingBloomFilter(m, k)

    cbf.insert(29)
    print(f"This gives us the state: {cbf.get_state()}.")
    cbf.insert(47)
    print(f"This gives us the state: {cbf.get_state()}.")
    cbf.insert(88)
    print(f"This gives us the state: {cbf.get_state()}.") 
    cbf.delete(88)
    print(f"This gives us the state: {cbf.get_state()}.")
    cbf.insert(39)
    print(f"This gives us the state: {cbf.get_state()}.")
"""
