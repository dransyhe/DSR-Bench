import random
from collections import OrderedDict

# For each mode, create a file and simulate an LRU cache with a series of page accesses.
path = "generation/lru_cache/cache"
for mode in ["easy", "medium", "hard"]:
    with open(f"{path}/lru_{mode}.txt", "w") as f:
        # Perform 30 simulation runs per mode
        for i in range(30):
            # Determine the number of operations and the cache size based on the mode.
            if mode == "easy":
                n = random.randint(5, 10)     # Number of page accesses
                k = random.randint(2, 5)      # Cache size is smaller for "easy"
                num_pages = 10
            elif mode == "medium":
                n = random.randint(11, 20)    # Number of page accesses
                k = random.randint(3, 7)      # A moderate cache size for "medium"
                num_pages = 20
            else:  # "hard"
                n = random.randint(21, 30)    # More page accesses for "hard"
                k = random.randint(4, 10)     # Larger cache size for "hard"
                num_pages = 30
            
            f.write(f"LRU Cache Simulation {i}, Cache Size: {k} \n")
            
            # Initialize an empty LRU cache using an OrderedDict
            lru = OrderedDict()
            
            # Simulate a sequence of page accesses.
            for _ in range(n):
                # Randomly choose a page number (for example, pages between 0 and 20)
                page = random.randint(0, num_pages - 1)
                f.write(f"access {page}\n")
                
                if page in lru:
                    # Page already in cache: mark it as most recently used by moving it to the end.
                    lru.move_to_end(page)
                else:
                    # If the cache is full, remove the least recently used (first) page.
                    if len(lru) >= k:
                        lru.popitem(last=False)
                    # Insert the new page into the cache.
                    lru[page] = True
            
            # The final state of the cache as a list (from least recently used to most recently used)
            final_cache = list(lru.keys())
            f.write("Final Cache: " + str(final_cache) + "\n")
