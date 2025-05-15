import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import list_to_str, parse_arguments, levenshtein

from evaluation.binary_tree.schema import InsertSchema, InsertSchemaAnsOnly, get_description


def main():

    args = parse_arguments()
    args.type = "binary_tree"
    args.operation = "remove"

    description = get_description(args)
        
    # We first collect all nodes to remove
    nodes_to_remove = []
    pre_truths = []
    post_truths = []
    with open(f"generation/binary_tree/remove/bst_remove_{args.mode}.txt", "r") as f:
        for line in f:
            if "Remove" in line:
                node_to_remove = line[line.index(":") + 2:-1]
                while node_to_remove[-1] == " ":
                    node_to_remove = node_to_remove[:-1]
                node_to_remove = int(node_to_remove)
                nodes_to_remove.append(node_to_remove)
            if "Pre" in line:
                nums = line[line.index(":")+ 2:-1]
                while nums[-1] == " ":
                    nums = nums[:-1]
                pre_truths.append(nums)
            elif "Post" in line:
                nums = line[line.index(":") + 2:-1]
                while nums[-1] == " ":
                    nums = nums[:-1]
                post_truths.append(nums)

    i = 0
    tree_index = -1
    Q_list = []
    with open(f"generation/binary_tree/bst_generation/bst_input_{args.mode}.txt", "r") as f:
        # Read in the tree
        lines = f.readlines()
        while i < len(lines):
            if i < len(lines) and "Tree" in lines[i]:
                root = None
                Q_state = description + "You should create a binary search tree. \n "
                i += 1
                tree_index += 1
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
            
            # Q += (
            #         f"\nYou would now like to remove a node with value {nodes_to_remove[tree_index]} from this binary search tree. \n"
            #         + "After the deletion, answer the following questions.  \n"
            #         + "Your answer to the following questions should be indexed. \n"
            #         + "Final answers to all questions should be wrapped by a single '<answer>' and '</answer>' tag. \n"
            #         + "1. What is the pre-order traversal of the current tree?\n"
            #         + "2. What is the post-order traversal of current tree?\n"
            #         + """For all two questions, your answer should only include a list of numbers
            #     in "[" and "]", where the numbers indicating the Node index are separated by ','.\n"""
            #     )

            Q += (
                f"\nYou would now like to remove a node with value {nodes_to_remove[tree_index]} from this binary search tree. Removal should preserve \n"
                    + "the validity of a binary search tree. After the removal, return the answer the following questions.  \n"
                    + "What is the pre-order traversal of the current tree?\n"
                    + "What is the post-order traversal of current tree?\n"
            )
            
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": {"pre_order": [56, 23, 78], "post_order": [23, 56, 78]} \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": {"pre_order": [56, 23, 78], "post_order": [23, 56, 78]}  \n' +\
                                '}\n '

            Q = translate(Q, Q_state, args)

            Q_list += [Q]

    deleteSchema = InsertSchemaAnsOnly if args.prompt == "AnsOnly" else InsertSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, deleteSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, deleteSchema)
        else:
            raise Exception("Invalid format type.")

    pre_answers = []
    post_answers = []

    for i, answer in enumerate(answers):
        try:
            js_answer = json.loads(answer)
        except Exception as e:
            print(f"Error encountered at index {i}: {e}")
            pre_answers.append("")
            post_answers.append("")
            continue 
        
        try:
            pre_answers.append(js_answer["final_answer"]["pre_order"])
        except Exception as e:
            print(f"We encountered error {e} while processing the answer: {js_answer}")
            pre_answers.append("")
            
        try:
            post_answers.append(js_answer["final_answer"]["post_order"])
        except Exception as e:
            print(f"We encountered error {e} while processing the answer: {js_answer}")
            post_answers.append("")

        if len(post_answers) != len(pre_answers):
            raise Exception("Post order length does not match with that of pre order.")

    score = []
    partial_score = []

    for i in range(len(pre_answers)):
        if list_to_str(pre_answers[i]) == pre_truths[i] and list_to_str(post_answers[i]) == post_truths[i]:
            score.append(1)
        else:
            score.append(0)
        pre_score = 1 - levenshtein(list_to_str(pre_answers[i]), pre_truths[i])
        post_score = 1 - levenshtein(list_to_str(post_answers[i]), post_truths[i])
        partial_score.append((pre_score + post_score)/2)
     
    log(Q_list, score, partial_score, answers, args)

if __name__ == "__main__":
    main()
