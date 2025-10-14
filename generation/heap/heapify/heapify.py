import random

def heapify(arr):
    n = len(arr)

    def sift_down(i):
        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = i

            if left < n and arr[left] < arr[smallest]:
                smallest = left
            elif left < n and arr[left] == arr[smallest]:
                smallest = left  # Tie-breaker: prefer left

            if right < n and arr[right] < arr[smallest]:
                smallest = right

            if smallest != i:
                arr[i], arr[smallest] = arr[smallest], arr[i]
                i = smallest
            else:
                break

    for i in range((n // 2) - 1, -1, -1):  # Bottom-up
        sift_down(i)

def generate_random_heap(n):
    arr = [random.randint(0, 100) for _ in range(n)]
    input_arr = arr.copy()
    heapify(arr)
    return input_arr, arr

for mode in ["easy", "medium", "hard"]:
    with open(f"heapify_{mode}.txt", "w") as f:
        for i in range(30):  
            if mode == "easy":
                n = random.randint(5, 10)
            elif mode == "medium":
                n = random.randint(11, 20)
            else:
                n = random.randint(21, 30)

            f.write(f"Heap {i}\n")

            input_arr, heap = generate_random_heap(n)
            input_str = "[" + ", ".join(map(str, input_arr)) + "]\n"
            heap_str = "[" + ", ".join(map(str, heap)) + "]\n"

            f.write(input_str)
            f.write(heap_str)
