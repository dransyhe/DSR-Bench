import numpy.random as random

class HashMap:
    def __init__(self, bucket_count):
        """
        Initialize the HashMap with a fixed number of buckets.
        In a real implementation, you would resize as elements grow.
        """
        self.bucket_count = bucket_count
        # Each bucket is a list of (key, value) pairs
        self.buckets = [[] for _ in range(bucket_count)]
        self.size = 0  # How many key-value pairs are stored

    def _hash_function(self, key):
        """
        Return a bucket index based on Python's built-in hash for the key.
        Note: hash() can vary across Python runs unless you set a hash seed.
        """
        return hash(key) % self.bucket_count

    def insert(self, key, value):
        """
        Insert or update the value for a given key.
        """
        index = self._hash_function(key)
        bucket = self.buckets[index]

        # Check if key already exists in the bucket
        for i, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                # Key found; update the value
                bucket[i] = (key, value)
                return

        # If key not found, append a new (key, value) pair
        bucket.append((key, value))
        self.size += 1

    def get(self, key):
        """
        Return the value for the given key, or None if key not in map.
        """
        index = self._hash_function(key)
        bucket = self.buckets[index]

        for (existing_key, val) in bucket:
            if existing_key == key:
                return val
        return None

    def remove(self, key):
        """
        Remove the (key, value) pair from the map, if it exists.
        Return True if removed, False if key not found.
        """
        index = self._hash_function(key)
        bucket = self.buckets[index]

        for i, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                del bucket[i]  # Remove the pair from the list
                self.size -= 1
                return True
        return False

    def __repr__(self):
        """
        Return a string representation of the HashMap for debugging.
        """
        buckets = []
        for bucket in self.buckets:
            pairs = []
            for key, value in bucket:
                pairs.append(f"({key}, {value})")
            buckets.append("[" +", ".join(pairs)+ "]")
        return "[" + ", ".join(buckets) + "]"
    
def generate_hashmap(size, num_buckets):
    hm = HashMap(bucket_count=num_buckets)
    for i in range(size):
        key = random.randint(0, 100)
        value = random.randint(0, 100)
        hm.insert(key, value)
    return hm

if __name__ == "__main__":
    
    path = "generation/hashmap/compound"
    for mode in ["easy", "medium", "hard"]:
        print(f"Generating compound_{mode}.txt")
        with open(f"{path}/compound_{mode}.txt", "w") as f:
            if mode == "easy":
                min_num_op = 5
                max_num_op = 10
                num_buckets = 10
            elif mode == "medium":
                min_num_op = 11
                max_num_op = 20 
                num_buckets = 20
            else:  
                min_num_op = 21
                max_num_op = 30
                num_buckets = 30
            
            for i in range(30):
                f.write(f"HashMap {i} with {num_buckets} buckets \n")
                
                hm = HashMap(bucket_count=num_buckets)
                list_keys = []
                
                num_op = random.randint(min_num_op, max_num_op)
                for _ in range(num_op):
                    p = random.uniform(0, 1)
                    if p < 0.7:
                        operation_type = "add"
                    else:
                        operation_type = "remove"
            
                    if operation_type == "add" or hm.size == 0:
                        value = random.randint(0, 100)
                        key = random.randint(0, 100)
                        list_keys.append(key)
                        hm.insert(key, value)
                        f.write(f"add key {key} value {value} \n")
                    
                    elif operation_type == "remove":
                        key = random.choice(list_keys)
                        hm.remove(key)
                        f.write(f"remove {key} \n")
                        
                f.write(f"Final HashMap: {hm} \n")
                f.write("\n")