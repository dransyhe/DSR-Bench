import os
import ast
import json
import random
import argparse
from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments

from natural.bst.schema import BSTSchema, BSTSchemaAnsOnly

from evaluation.utils import levenshtein

# a fresh set of first names
extra_first_names = [
    "Brandon", "Sydney", "Kai", "Nia", "Zara",
    "Ravi", "Leila", "Jasper", "Beatrix", "Orion"
]

# a fresh set of surnames
extra_surnames = [
    "Owens", "McCarthy", "Bloom", "Choi", "Freeman",
    "Patterson", "Solomon", "Torres", "Ueda", "Ivanov"
]

extra_pool = [f"{fn} {ln}" 
              for fn in extra_first_names 
              for ln in extra_surnames]

def str_to_minutes(t: str) -> int:
    h, m = map(int, t.split(":"))
    return h * 60 + m

def minutes_to_str(m: int) -> str:
    h, mm = divmod(m, 60)
    return f"{h:02d}:{mm:02d}"

def main():
    args = parse_arguments()
    args.type = "bst"
    args.operation = "natural"

    # ——— paths ———
    module_dir   = "./natural/bst/"
    os.makedirs(module_dir, exist_ok=True)

    nat_path     = os.path.join(module_dir, f"natural-{args.mode}.txt")
    desc_path    = os.path.join(module_dir, "template", "description.txt")
    insert_path  = os.path.join(module_dir, "template", "insert.txt")
    delete_path  = os.path.join(module_dir, "template", "delete.txt")

    # ——— load operations + truths ———
    with open(nat_path, "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    # pool of all inserted names & times
    all_names = []
    all_times = []
    for L in lines:
        if L.startswith("insert"):
            _, name, time = L.split(" ", 2)
            all_names.append(name)
            all_times.append(time)

    # ——— load templates & descriptions ———
    with open(desc_path)   as f: descriptions    = [l.strip() for l in f if l.strip()]
    with open(insert_path) as f: insert_tmpls   = [l.strip() for l in f if l.strip()]
    with open(delete_path) as f: delete_tmpls   = [l.strip() for l in f if l.strip()]

    Q_list = []
    truths = []
    i = 0
    while i < len(lines):
       # 1) pick a description
        description = random.choice(descriptions)
        Q = description + "Initially the tree is empty.\n\n"
        used_names = []
        bst_names = []
        used_times = []

        # 2) consume ops until the truth‐list (line starting with “[”)
        while i < len(lines) and not lines[i].startswith("["):
            op_line = lines[i].strip()
            parts = op_line.split() 

            if parts[0] == "insert":
                # parse name = all but first and last, time = last
                name = " ".join(parts[1:-1])
                time = parts[-1]

                tmpl = random.choice(insert_tmpls)
                filled = tmpl.replace("{name}", name)
                filled = filled.replace("{time}", time)

                if "{name_prev}" in filled:
                    prev = random.choice(used_names) if used_names else "some other patient"
                    filled = filled.replace("{name_prev}", prev)

                if "{extra_name}" in filled:
                    pool = [n for n in extra_pool if n not in used_names and n != name]
                    extra = random.choice(pool) if pool else "some other patient"
                    filled = filled.replace("{extra_name}", extra)

                if "{time_prev}" in filled:
                    cur = str_to_minutes(time)
                    delta = random.randint(1, min(cur, 60))
                    tp = minutes_to_str(cur - delta)
                    filled = filled.replace("{time_prev}", tp)

                if "{time_after}" in filled:
                    cur = str_to_minutes(time)
                    delta = random.randint(1, min(60, 23*60+59 - cur))
                    ta = minutes_to_str(cur + delta)
                    filled = filled.replace("{time_after}", ta)

                Q += filled + "\n"
                used_names.append(name)
                bst_names.append(name)
                used_times.append(time)

            elif parts[0] == "delete":
                # parse name = everything after the first token
                name = " ".join(parts[1:])
                tmpl = random.choice(delete_tmpls)
                filled = tmpl.replace("{name}", name)
                if "{name_prev}" in filled:
                    prev = random.choice(used_names) if used_names else "some other patient"
                    filled = filled.replace("{name_prev}", prev)
                if "{extra_name}" in filled:
                    pool = [n for n in bst_names if n != name]
                    extra = random.choice(pool) if pool else "some other patient"
                    filled = filled.replace("{extra_name}", extra)
                Q += filled + "\n"

            i += 1

        # collect the truth and advance past it
        truths.append(lines[i])
        i += 1

        # append the final question
        Q += (
            "Q: What is the pre-order traversal of the appointment schedule "
            "following the binary search tree? Your answer should be a list of "
            "(name, appointment time) in the format of a tuple of two strings.\n"
        )
        # translate/format prompt
        Q_list.append(translate(Q, description, args))

    # run prediction/evaluation
    bstSchema = BSTSchemaAnsOnly if args.prompt == "AnsOnly" else BSTSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, bstSchema)
    else:
        if args.format == "schema":
            answers = predict(Q_list, args, bstSchema)
        else:
            raise Exception("Invalid format type.")

    # compare against truths
    res = []
    partial_res = []
    for idx, ans_text in enumerate(answers):
        try:
            js = json.loads(ans_text)
            ans = js["final_answer"]
        except Exception as e:
            print(f"Error parsing answer at idx {idx}: {e}")
            res.append(0)
            partial_res.append(0)
            continue

        truth_list = ast.literal_eval(truths[idx])   
        ans_list = [tuple(x) for x in ans]     

        if truth_list == ans_list:
            res.append(1)
        else:
            res.append(0)
            print(f"Answer: {ans_list}")
            print(f"Truth: {truth_list}")
        partial_res.append(1 - levenshtein(str(ans_list), str(truth_list)))

    log(Q_list, res, partial_res, answers, args)


if __name__ == "__main__":
    main()
