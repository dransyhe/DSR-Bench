import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.eval import prompt_list, model_list
from evaluation.utils import list_to_str, parse_arguments, levenshtein

from evaluation.kd_tree.schema import KDTSchema, KDTSchemaAnsOnly


def main():

    args = parse_arguments()
    args.type = "kd_tree"
    
    dim = args.dim
    
    args.operation = f"construct_d{args.dim}"

    i = 0
    Q_list = []

    post_truths = []
    
    # data_dist = 'moon' # 'circle', 'moon', 'blobs', 'unif'
    # dim = 3 # 2, 3, 5
    # dg = 3 # 3, 5
    
    # with open(f"generation/kd_tree/construction/{data_dist}_kdt_construct_{args.mode}.txt", "r") as f:
    # with open(f"generation/kd_tree/construction/{dg}dg_kdt_construct_{args.mode}.txt", "r") as f:
    with open(f"generation/kd_tree/construct_{dim}d/construct_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        if args.description == "full":
            description = "A k‑dimensional tree (KD‑tree) is a binary space‑partitioning data structure for organizing points in R^k. \n" + \
                "Starting with the entire point set, it recursively divides space by hyperplanes that are perpendicular to one of the coordinate axes: \n" + \
                "at each node a splitting dimension is chosen by cycling through the k axes, a split value is selected at the median along that dimension, \n" + \
                " and the node’s two children hold the points on either side of that hyperplane. \n" + \
                "Suppose you have an empty KD tree. You should construct a KD tree with a set of given points \n " + \
                "by splitting the x-axis (1st axis) first, then the y_axis (2nd axis), then the 3rd, then 4th, ... \n" +\
                "And loop back to x-axis if you splitcted with the last axis possible. For median of even numbers, always \n" +\
                "Use the latter one in the middle as the median (i.e. median of [1, 2] is 2, and median of [8, 6, 3, 4] is 6)."
        else:
            description = "Suppose you have an empty KD tree. You should construct a KD tree with a set of given points \n " + \
                "by splitting the x-axis (1st axis) first, then the y_axis (2nd axis), then the 3rd, then 4th, ... \n" +\
                "And loop back to x-axis if you splitcted with the last axis possible. For median of even numbers, always \n" +\
                "Use the latter one in the middle as the median (i.e. median of [1, 2] is 2, and median of [8, 6, 3, 4] is 6)."
        Q_state = description
        
        if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": [[56, 23], [78, 62], [67, 25]] \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": [[56, 23], [78, 62], [67, 25]] \n' +\
                                '}\n '
        
        while i < len(lines):
            
            if "Points" in lines[i]:
                points = lines[i].split(":")[1]
                Q = f"Construct a KD-tree with the following points: {points}\n"
                Q += f"If there's ever ties when sorting an axis, such as [56, 32] and [56, 12] when sortinhg by x-axis, please keep the original order in the given data."
                Q += "After that, please answer the following question:\n" + \
                    "Q: What is the pre-order traversal of the tree? Output in a nested list like the input. \n"
                i += 1
                # print(f"Q: {Q}")
                Q = translate(Q, Q_state, args)
                Q_list += [Q]
            elif "Traversal" in lines[i]:
                values = lines[i].split(":")[1].strip()
                post_truths.append(values)
                i += 1
            elif "Tree" in lines[i]:
                i += 1
                pass

    traverseSchema = KDTSchemaAnsOnly if args.prompt == "AnsOnly" else KDTSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, traverseSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, traverseSchema)
        else:
            raise Exception("Invalid format type.")
        
    post_answers = []
    for answer in answers:
        try:
            js_answer = json.loads(answer)
            post_answers.append(js_answer["final_answer"])
        except Exception as e:
            print(f"Error encountered probably due to short of tokens.")
            post_answers.append("")
            continue
        
    score = []
    partial_score = []

    for i in range(len(post_answers)):
        if list_to_str(post_answers[i]).strip() == list_to_str(post_truths[i]).strip():
            score.append(1)
        else:
            score.append(0)
            # print(repr(list_to_str(post_answers[i]).strip()))
            # print(repr(list_to_str(post_truths[i]).strip()))
        partial_score.append(1 - levenshtein(list_to_str(post_answers[i]).strip(), list_to_str(post_truths[i]).strip()))
 
    log(Q_list, score, partial_score, answers, args)

if __name__ == "__main__":
    main()
