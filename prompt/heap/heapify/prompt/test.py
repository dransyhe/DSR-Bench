import heapq 

def min_heapify(arr):
    """Turn an array into a min-heap and print intermediate states."""
    n = len(arr)

    # Start from the last non-leaf node and heapify downwards
    for i in range(n // 2 - 1, -1, -1):
        print(f"Start from the last non-leaf node {arr[i]} at index {i}.")
        sift_down(arr, i, n)
        print(f"Heap after heapifying index {i}: {arr}")  # Print intermediate state

def sift_down(arr, i, n):
    """Heapify subtree rooted at index i in an array of size n."""
    smallest = i  # Assume root is smallest
    left = 2 * i + 1  # Left child
    right = 2 * i + 2  # Right child
    print(f"For the current subtree, root is {arr[i]}, assume it is the smallest.")

    # Check if left child exists and is smaller than root
    if left < n and arr[left] < arr[smallest]:
        print(f"Its left child {arr[left]} is smaller than the current smallest {arr[smallest]}.")
        smallest = left

    # Check if right child exists and is smaller than the smallest so far
    if right < n and arr[right] < arr[smallest]:
        print(f"Its right child {arr[right]} is smaller than the current smallest {arr[smallest]}.")
        smallest = right

    # If smallest is not the root, swap and continue heapifying
    if smallest != i:
        print(f"Root is not the smallest, swap {arr[i]} with {arr[smallest]} and continue heapifying recursivly.")
        arr[i], arr[smallest] = arr[smallest], arr[i]
        sift_down(arr, smallest, n)  # Recursive call
    else: 
        print("Root is smallest, no more heapifying needed for the current subtree.")

# Example usage
arr = [71, 32, 100, 52, 21]
array = arr.copy()
print("Original array:", arr)
min_heapify(arr)
print("Final Min-Heap:", arr)

heapq.heapify(array)
print("Python heapify", array)  # Check with Python's heapify function