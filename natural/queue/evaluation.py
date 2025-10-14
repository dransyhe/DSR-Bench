import openai
import os
import argparse
import ast  
import json
import random

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments

from evaluation.utils import levenshtein

from natural.queue.schema import QueueSchema, QueueSchemaAnsOnly

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


def main():
    args = parse_arguments()
    args.type = "queue"
    args.operation = "natural"

    # locate files relative to this script
    base_dir = os.path.dirname(__file__)
    natural_path    = os.path.join(base_dir, f"natural-{args.mode}.txt")
    desc_path       = os.path.join(base_dir, "template", "description.txt")
    enqueue_path    = os.path.join(base_dir, "template", "enqueue.txt")
    dequeue_path    = os.path.join(base_dir, "template", "dequeue.txt")

    # (i) load the operations + truths
    with open(natural_path, "r") as f:
        nat_lines = [l.strip() for l in f if l.strip()]
    # extract the full pool of names for sampling extras
    all_names = [l.split(" ",1)[1] for l in nat_lines if l.startswith("enqueue")]

    # (ii) load 5 descriptions
    with open(desc_path, "r") as f:
        descriptions = [l.strip() for l in f if l.strip()]

    # (iii) load enqueue templates
    with open(enqueue_path, "r") as f:
        enqueue_templates = [l.strip() for l in f if l.strip()]

    # (iv) load dequeue templates
    with open(dequeue_path, "r") as f:
        dequeue_templates = [l.strip() for l in f if l.strip()]

    truths = []
    Q_list = []
    i = 0

    while i < len(nat_lines):
        # sample one description
        description = random.choice(descriptions)

        Q = description + "\n\n"
        used_names = []

        # consume operations until final-state line (starts with “[”)
        while i < len(nat_lines) and not nat_lines[i].startswith("["):
            op_line = nat_lines[i]
            if op_line.startswith("enqueue"):
                # parsed name
                _, name = op_line.split(" ", 1)

                # pick and fill an enqueue template
                tmpl = random.choice(enqueue_templates)
                filled = tmpl.replace("{name}", name)

                # if template has {name_prev}, pick from previously used names
                if "{name_prev}" in filled:
                    prev = random.choice(used_names) if used_names else "some other kid"
                    filled = filled.replace("{name_prev}", prev)

                # if template has {extra_name}, pick from names not yet used
                if "{extra_name}" in filled:
                    pool = [n for n in extra_pool if n not in used_names and n != name]
                    extra = random.choice(pool) if pool else "some other kid"
                    filled = filled.replace("{extra_name}", extra)

                Q += filled + "\n"
                used_names.append(name)

            elif op_line.startswith("dequeue"):
                # pick a dequeue template and append
                tmpl = random.choice(dequeue_templates)
                Q += tmpl + "\n"
            else:
                # skip any unexpected lines
                pass

            i += 1

        # now nat_lines[i] is the truth list
        truths.append(nat_lines[i])
        i += 1

        # finally, add the question
        Q += "\nQ: What is the order of the remaining kids in line? Your answer should be a list of names.\n"
        
        # translate or format prompt as before
        Q_formatted = translate(Q, description, args)
        Q_list.append(Q_formatted)

    # run prediction/evaluation
    queueSchema = QueueSchemaAnsOnly if args.prompt == "AnsOnly" else QueueSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, queueSchema)
    else:
        if args.format == "schema":
            answers = predict(Q_list, args, queueSchema)
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

        truth = ast.literal_eval(truths[idx])   
        # ans_list   = ast.literal_eval(ans)          

        if ans == truth:
            res.append(1)
        else:
            res.append(0)
            print(f"Answer: {ans}")
            print(f"Truth: {truth}")
        partial_res.append(1 - levenshtein(ans, truth))

    log(Q_list, res, partial_res, answers, args)


if __name__ == "__main__":
    main()
