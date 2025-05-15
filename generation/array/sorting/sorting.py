def num_to_str(generated_list, f):
    input = "["
    for num in generated_list[:-1]:
        input = input + str(num) + ","
    input = input + str(generated_list[-1]) + "]" + "\n"
    f.write(input)

def insertionSort(arr, f):
    n = len(arr)  # Get the length of the array

    if n <= 1:
        return  # If the array has 0 or 1 element, it is already sorted, so return

    for i in range(1, n):  # Iterate over the array starting from the second element
        key = arr[i]  # Store the current element as the key to be inserted in the right position
        j = i - 1
        while j >= 0 and key < arr[j]:  # Move elements greater than key one position ahead
            arr[j + 1] = arr[j]  # Shift elements to the right
            j -= 1
        arr[j + 1] = key  # Insert the key in the correct position
    num_to_str(arr, f)


for mode in ["easy", "medium", "hard"]:

    with open(f"../array_input_{mode}.txt", "r") as f:
        f_write = open(f"sorted_{mode}.txt", "w")
        for i, input in enumerate(f):
            # f_write.write(str(i)+"\n")
            # f_write.write(input)
            num = [int(i) for i in input[1:-2].split(",") if i.isdigit()]
            insertionSort(num, f_write)


