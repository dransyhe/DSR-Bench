def num_to_str(generated_list, f):
    input = "["
    for num in generated_list[:-1]:
        input = input + str(num) + ","
    input = input + str(generated_list[-1]) + "]" + "\n"
    f.write(input)

import random

for mode in ["easy", "medium", "hard"]:

    with open(f"../array_input_{mode}.txt", "r") as f:
        f_write = open(f"search_{mode}.txt", "w")
        for i, input in enumerate(f):
            f_write.write(str(i)+"\n")
            f_write.write(input)
            num = [int(i) for i in input[1:-2].split(",")]
            n = len(num)
            index = random.randint(0, n - 1)
            element = num[index]
            index = num.index(element)
            f_write.write(f"Element: {element}\n")
            f_write.write(f"Answer: {index}\n")

    # NOTE: in prompt, says the first element if duplicated

