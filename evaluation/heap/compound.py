import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

from evaluation.heap.schema import HeapSchema, HeapSchemaAnsOnly


def main():

    args = parse_arguments()
    args.type = "heap"
    args.operation = "compound"

    truths = []

    i = 0
    Q_list = []
    with open(f"generation/heap/compound/compound_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            i += 1

            if args.description == "full":
                description = (
                    "A min-heap is a binary tree-based data structure that satisfies the heap property: every parent node is less than or equal to its children.\n" + \
                    "It is implemented as an array-based binary heap.\n" + \
                    "It has two operations:\n" + \
                    "1. (insert, k) appends an element k to the heap by:\n" + \
                    "   a. Adding the element to the end of the array.\n" + \
                    "   b. Swapping it with its parent while it is smaller, until it is in the correct position or becomes the root.\n" + \
                    "2. (delete) removes the root element:\n" + \
                    "   a. Replace the root with the last element in the array.\n" + \
                    "   b. Swap it with its smaller child while it is larger, preferring the left child in case of a tie, until it is in the correct position or becomes a leaf.\n"
                )
            else: 
                description = \
                    "A min-heap has two operations:\n" + \
                    "1. (insert, k) appends an element k to the heap.\n" + \
                    "2. (delete) removes the root element.\n" + \
                    "The heap is implemented as an array-based binary heap.\n" + \
                    "The heap property is maintained after each operation.\n" + \
                    "When bubbling down during deletion, prefer the left child in case of a tie.\n"

            Q_state = description + \
                "You are given an empty heap initially. You should use a min-heap with array-based implementation. \n" + \
                "If a node has two children, the left child must be smaller than (or equal to) the right child. \n"

            Q = "Q: What is the state of the heap after the following operations: \n"

            while i < len(lines) and "[" not in lines[i]:
                if "insert" in lines[i]:
                    num = int(lines[i].split(" ")[-1])
                    Q += f"(insert, {num})\n"
                elif "delete" in lines[i]:
                    Q += "(delete)\n"
                i += 1

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
                                
            Q = translate(Q, Q_state, args)

            truths.append(lines[i].strip())
            Q_list += [Q]
            i += 1

    heapSchema = HeapSchemaAnsOnly if args.prompt == "AnsOnly" else HeapSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, heapSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, heapSchema)
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
        if str(answer) == str(truths[i]):
            res.append(1)
        else:
            res.append(0)
        partial_res.append(1 - levenshtein(str(answer), str(truths[i])))

    log(Q_list, res, partial_res, answers, args)


if __name__ == "__main__":
    main()

