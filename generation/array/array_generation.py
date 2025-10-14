import random

for mode in ["easy", "medium", "hard"]:
    with open(f"array_input_{mode}.txt", "w") as f:
        if mode == "easy":
            max_length = 10
        elif mode == "medium":
            max_length = 20
        else:
            max_length = 30

        # generate random numbers range from 0 to 100 
        numbers = [random.randint(0, 100) for _ in range(max_length)]

        for _ in range(30):
            if mode == "easy":
                length = random.randint(5, 10)
            elif mode == "medium":
                length = random.randint(11, 20)
            else:
                length = random.randint(21, 30)
            generated_list = random.choices(numbers, k=length)
            input = "["
            for num in generated_list[:-1]:
                input = input + str(num) + ", "
            input = input + str(generated_list[-1]) + "]" + "\n"
            f.write(input)
