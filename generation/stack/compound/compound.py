def num_to_str(generated_list, f):
    input = "["
    for num in generated_list[:-1]:
        input = input + str(num) + ", "
    input = input + str(generated_list[-1]) + "]" + "\n"
    f.write(input)

import random

for mode in ["easy", "medium", "hard"]:

    with open(f"compound_{mode}.txt", "w") as f:
        for _ in range(30):
            if mode == "easy":
                length = random.randint(5, 10)
            elif mode == "medium":
                length = random.randint(11, 20)
            else:
                length = random.randint(21, 30)
            stack = []
            for _ in range(length):
                op = random.random()
                if len(stack) == 0:
                    op = 0
                if op < 0.7:
                    element = random.randint(0, 100)
                    f.write(f"push {element}\n")
                    stack.append(element)
                else:
                    stack.pop()
                    f.write("pop\n")
            if len(stack) > 0:
                num_to_str(stack, f)
            else:
                f.write("[]\n")



