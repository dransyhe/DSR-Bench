import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

from evaluation.stack.schema import StackSchema, StackSchemaAnsOnly


def main():

    args = parse_arguments()
    args.type = "stack"
    args.operation = "compound"

    truths = []

    i = 0
    Q_list = []
    with open(f"generation/stack/compound/compound_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):

            if args.description == "full":
                description = ("A stack is a data structure in which items are added and removed at the same end, maintaining a first-in, last-out (FILO) order. \n"
                        "You should create a stack. \n There are two types of operations: \n" 
                        "1. (push, k) appends an element k to the stack as the last element. \n " 
                        "2. (pop) removes the last element in the stack. \n" 
                )
            else:
                description = (
                        "You should create a stack. \n There are two types of operations: \n" 
                        "1. (push, k) adds an element k to the stack. \n " 
                        "2. (pop) removes the next element from the stack. \n" 
                )

            Q_state = description + (
               "You are given an empty stack initially. \n"
            )

            Q = " Q: What is the state of the stack after the following operations: \n"

            while i < len(lines) and "[" not in lines[i]:
                if "push" in lines[i]:
                    num = int(lines[i].split(" ")[-1])
                    Q += f"(push, {num})\n"
                elif "pop" in lines[i]:
                    Q += "(pop)\n"
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

            truths.append(lines[i][:-1])
            Q_list += [Q]
            i += 1

    stackSchema = StackSchemaAnsOnly if args.prompt == "AnsOnly" else StackSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, stackSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, stackSchema)
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

