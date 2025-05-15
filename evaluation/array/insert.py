import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

from evaluation.array.schema import DeleteSchema, DeleteSchemaAnsOnly, get_description


def main():

    args = parse_arguments()
    args.type = "array"
    args.operation = "insert"


    arrays = []
    with open(f"generation/array/array_input_{args.mode}.txt", "r") as f:
        for input in f:
            arrays.append(input[:-1])

    indices = []
    truths = []
    elements = []
    counter = 0
    with open(f"generation/array/insert/insert_{args.mode}.txt", "r") as f:
        for line in f:
            if counter == 2:
                index = line[:-1].split(" ")[-1]
                indices += [index]
            elif counter == 3:
                element = line[:-1].split(" ")[-1]
                elements += [element]
            elif counter == 4:
                truth = line[line.index(":") + 2:]
                truths += [truth.strip()]
            counter = (counter + 1) % 5

    Q_list = []
    for i in range(len(arrays)):
        Q_state = get_description(args)
        
        if "deepseek-chat" in args.model:
            if args.prompt == "AnsOnly":
                Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                        '{ \n' +\
                        '    "final_answer": [32, 10, 83, 28] \n' +\
                        '}\n '
            else:
                Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                            '    "final_answer": [32, 10, 83, 28]  \n' +\
                            '}\n '
                            
        Q = f"Given an array {arrays[i]}. Insert an item of value {elements[i]} at index {indices[i]}. Q: What is the updated array? \n" 
        # Q = Q + "Your final answer should be a list [item1, item2, ...] wrapped by '<answer>' and '</answer>' tags. \n"
        Q = translate(Q, Q_state, args)
        Q_list.append(Q)
        
    if args.batch:
        if args.prompt == "AnsOnly":
            answers = get_batch_results(Q_list, args, DeleteSchemaAnsOnly)
        else:
            answers = get_batch_results(Q_list, args, DeleteSchema)
    else: 
        if args.format == "schema":
            if args.prompt == "AnsOnly":
                answers = predict(Q_list, args, DeleteSchemaAnsOnly)
            else:
                answers = predict(Q_list, args, DeleteSchema)
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

