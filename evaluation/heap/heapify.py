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
    args.operation = "heapify"

    
    i = 0
    Q_list = []
    truths = []
    with open(f"generation/heap/heapify/heapify_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            array = lines[i + 1].strip().split(", ")
            array = ", ".join(array)

            if args.description == "full":
                description = (
                    "A min-heap is a complete binary tree where the value of each node is less than or equal to the values of its children.\n"
                    "A bottom-up heapify algorithm works by:\n"
                    "a. Starting from the last non-leaf node at index (n // 2) - 1, where n is the number of elements.\n"
                    "b. Iterating bottom-up from this index to index 0, in decreasing order.\n"
                    "c. For each node, compare it with its children and swap it with the smaller child if it is larger.\n"
                    "d. In case of a tie between children, prefer the left child.\n"
                    "e. Repeat the process for the swapped child until the heap property is satisfied."
                )
            else:
                description = (
                    "Use bottom-up heapify to convert an unsorted array into a min-heap.\n" + \
                    "The heap is implemented as a 0-indexed array-based binary heap.\n" + \
                    "Start from index (n // 2) - 1 and process nodes bottom-up in decreasing order.\n" + \
                    "For each node, restore the heap property by bubbling the value down.\n" + \
                    "When comparing children, prefer the left child in case of a tie.\n"
                )

            Q_state = description 
            
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
        
            Q = f"Q: Given an array {array}, turn it into a min-heap with array-based implementation. \n" + \
                "If a node has two children, the left child must be smaller than (or equal to) the right child. \n" 

            # Q = Q + "Your final answer should be a list [item1, item2, ...], which represents the heap, and wrapped by '<answer>' and '</answer>' tags. \n" 

            Q = translate(Q, Q_state, args) 

            Q_list += [Q]

            truths.append(lines[i + 2].strip())
            i += 3

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

