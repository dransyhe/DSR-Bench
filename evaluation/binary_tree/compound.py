import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, list_to_str, levenshtein

from evaluation.binary_tree.schema import CompoundSchema, CompoundSchemaAnsOnly, get_description


def main():

    args = parse_arguments()
    args.type = "binary_tree"
    args.operation = "compound"

    truths = []

    i = 0
    Q_list = []
    with open(f"generation/binary_tree/compound/bst_compound_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            
            description = get_description(args)

            Q_state = description + \
               "You are given an empty binary search tree. \n" + \
                "You should perform the following insert and delete operations. \n" + \
                "After performing all operations, return the pre-order traversal in a flattened list of the final tree. \n" 
            
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": [56, 23, 78] \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": [56, 23, 78] \n' +\
                                '}\n '

            Q = "Q: What is the final state of the binary search tree, after performing the following operations: \n"

            while i < len(lines) and "[" not in lines[i]:
                if "Insert" in lines[i]:
                    num = int(lines[i].split(" ")[-1])
                    Q += f"(insert, {num})\n"
                elif "Delete" in lines[i]:
                    num = int(lines[i].split(" ")[-1])
                    Q += f"(delete, {num})\n"
                i += 1

            Q = translate(Q, Q_state, args)
            truths.append(lines[i][:-1])
            Q_list += [Q]
            i += 1

    queueSchema = CompoundSchemaAnsOnly if args.prompt == "AnsOnly" else CompoundSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, queueSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, queueSchema)
        else:
            raise Exception("Invalid format type.")

    res = []
    partial_res = []
    for i in range(len(answers)):
        try:
            js_answer = json.loads(answers[i])
            answer = js_answer["final_answer"]
        except Exception as e:
            print(f"Error encountered at index {i}: {e}")
            res.append(0)
            partial_res.append(0)
            continue 
        if list_to_str(answer) == list_to_str(truths[i]):
            res.append(1)
        else:
            res.append(0)
            print(f"Answer: {list_to_str(answer)}")
            print(f"Truth: {list_to_str(truths[i])}")
        edit_dist = levenshtein(list_to_str(answer), list_to_str(truths[i]))
        partial_res.append(1 - edit_dist)
            
    log(Q_list, res, partial_res, answers, args)


if __name__ == "__main__":
    main()

