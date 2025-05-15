import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import list_to_str, parse_arguments, levenshtein

from evaluation.binary_tree.schema import TraverseSchema, TraverseSchemaAnsOnly, get_description


def main():

    args = parse_arguments()
    args.type = "binary_tree"
    args.operation = "inorder"

    description = get_description(args)
    
    i = 0
    Q_list = []
    with open(f"generation/binary_tree/bst_generation/bst_input_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            if i < len(lines) and "Tree" in lines[i]:
                root = None
                Q_state = description + "You should create a binary search tree. \n "
                i += 1
            while i < len(lines) and ("Tree" not in lines[i]):
                node, left, right = lines[i].strip().split(" ")
                if not root:
                    root = node
                    Q = f"Q: The root node is Node {node}. "
                if "None" not in left and "None" not in right:
                    Q += f"Node {node}'s left child is Node {left}, and its right child is Node {right}. "
                elif "None" not in left:
                    Q += f"Node {node}'s left child is Node {left}. "
                elif "None" not in right:
                    Q += f"Node {node}'s right child is Node {right}. "
                i += 1
            Q += "\n What is the in-order traversal of the tree? \n"
            
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

            Q_list += [Q]

    traverseSchema = TraverseSchemaAnsOnly if args.prompt == "AnsOnly" else TraverseSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, traverseSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, traverseSchema)
        else:
            raise Exception("Invalid format type.")

    in_answers = []

    for i, answer in enumerate(answers):
        try:
            js_answer = json.loads(answer)
            in_answers.append(js_answer["final_answer"])
        except Exception as e:
            print(f"Error encountered at index {i}: {e}")
            in_answers.append("")
            continue 

    in_truths = []

    with open(f"generation/binary_tree/traversal/bst_traversal_{args.mode}.txt", "r") as f:
        for line in f:
            if "In" in line:
                nums = line[line.index(":")+ 2:-1]
                while nums[-1] == " ":
                    nums = nums[:-1]
                in_truths.append(nums)

    score_in = []
    partial_score = []

    for i in range(len(in_answers)):
        if list_to_str(in_answers[i]) == in_truths[i]:
            score_in.append(1)
        else:
            score_in.append(0)
        partial_score.append(1 - levenshtein(list_to_str(in_answers[i]), in_truths[i]))

    log(Q_list, score_in, partial_score, answers, args)

if __name__ == "__main__":
    main()
