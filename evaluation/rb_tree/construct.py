import openai
import os
import argparse
import json
import ast

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import list_to_str, parse_arguments, levenshtein
from evaluation.tree_ted import ted_score

from evaluation.rb_tree.schema import (
    RBTreeSchema, RBTreeSchemaAnsOnly,
    RBTreeTEDSchema, RBTreeTEDSchemaAnsOnly,
)

TED_SUPPORTED = True


def main():

    args = parse_arguments()
    args.type = "rb_tree"
    args.operation = "construct"

    if args.ted and not TED_SUPPORTED:
        print("Warning: --ted is not supported for this task. Falling back to 0/1 scoring.")
        args.ted = False

    i = 0
    Q_list = []

    truths = []

    # Load ground-truth trees for TED mode from a pre-generated JSON file.
    if args.ted:
        with open(f"generation/rb_tree/construct/rbt_construct_{args.mode}_tree.json", "r") as f:
            truths_tree = json.load(f)

    with open(f"generation/rb_tree/construct/rbt_construct_{args.mode}.txt", "r") as f:
        lines = f.readlines()

        if args.description == "full":
            description = "A red-black tree is a self-balancing binary search tree. \n" + \
                "It has the following properties: \n" + \
                "1. Each node is either red or black. \n" + \
                "2. The root is always black. \n" + \
                "3. All leaves (NIL nodes) are black. \n" + \
                "4. Red nodes cannot have red children. \n" + \
                "5. Every path from a node to its descendant NIL nodes has the same number of black nodes. \n" + \
                "Inserting a value into a red-black tree involves the following steps: \n" + \
                "a) Insert the value as you would in a regular binary search tree. \n" + \
                "b) Color the new node red. \n" + \
                "c) Fix any violations of the red-black tree properties. \n"
        else:
            description = ""

        Q_state = description + \
            "Suppose you have an empty red-black tree. Construct a red-black tree by inserting the following values in order: "

        while i < len(lines):
            if "Values" in lines[i]:
                Q = lines[i].split(" ")[1]
                Q = f"{Q}\n"

                if args.ted:
                    Q += (
                        "Represent the final state of the red-black tree as a nested JSON object "
                        "with keys \"value\" (int), \"color\" (\"r\" or \"b\"), "
                        "\"left\" (subtree or null), and \"right\" (subtree or null).\n"
                        "Q: What is the final state of the red-black tree after construction? \n"
                    )
                    if "deepseek-chat" in args.model:
                        example = (
                            '{"value": 36, "color": "b", '
                            '"left": {"value": 21, "color": "b", "left": null, "right": null}, '
                            '"right": {"value": 66, "color": "r", "left": null, "right": null}}'
                        )
                        if args.prompt == "AnsOnly":
                            Q_state += 'EXAMPLE JSON OUTPUT: \n{ \n    "final_answer": ' + example + '\n}\n '
                        else:
                            Q_state += (
                                'EXAMPLE JSON OUTPUT: \n{ \n'
                                '    "steps": [{intermediate step 1}, ...], \n'
                                '    "final_answer": ' + example + '\n}\n '
                            )
                else:
                    Q += (
                        "The final state of the red-black tree should be a list of (value, color) pairs from \n"
                        "pre-order traversal of the tree, where color is either 0 (if 'r'), 1 (if 'b').\n"
                        "Q: What is the final state of the red-black tree after construction? \n"
                    )
                    if "deepseek-chat" in args.model:
                        if args.prompt == "AnsOnly":
                            Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                    '{ \n' +\
                                    '    "final_answer": [[56, 0], [67, 0], [78, 0]] \n' +\
                                    '}\n '
                        else:
                            Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                        '{ \n' +\
                                        '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                        '    "final_answer": [[56, 0], [67, 0], [78, 0]] \n' +\
                                        '}\n '

                Q = translate(Q, Q_state, args)
                Q_list += [Q]

            if "Pre-order" in lines[i]:
                values = lines[i][lines[i].index(":") + 2:]
                values = ast.literal_eval(values)
                color_map = {'r': 0, 'b': 1}
                converted = [[v, color_map[c]] for v, c in values]
                truths.append(converted)
            i += 1

    if args.ted:
        traverseSchema = RBTreeTEDSchemaAnsOnly if args.prompt == "AnsOnly" else RBTreeTEDSchema
    else:
        traverseSchema = RBTreeSchemaAnsOnly if args.prompt == "AnsOnly" else RBTreeSchema

    if args.batch:
        answers = get_batch_results(Q_list, args, traverseSchema)
    else:
        if args.format == "schema":
            answers = predict(Q_list, args, traverseSchema)
            print(answers)
        else:
            raise Exception("Invalid format type.")

    pre_answers = []
    for answer in answers:
        try:
            js_answer = json.loads(answer)
            pre_answers.append(js_answer["final_answer"])
        except Exception as e:
            print(f"Error encountered probably due to short of tokens.")
            pre_answers.append(None if args.ted else "")
            continue

    score = []
    partial_score = []

    for i in range(len(pre_answers)):
        if args.ted:
            s = ted_score(pre_answers[i], truths_tree[i])
            partial_score.append(s)
            score.append(1 if s == 1.0 else 0)
        else:
            if str(pre_answers[i]) == str(truths[i]):
                score.append(1)
            else:
                score.append(0)
                print(list_to_str(pre_answers[i]).strip())
                print(list_to_str(truths[i]).strip())
            partial_score.append(1 - levenshtein(str(pre_answers[i]), str(truths[i])))

    log(Q_list, score, partial_score, answers, args)

if __name__ == "__main__":
    main()
