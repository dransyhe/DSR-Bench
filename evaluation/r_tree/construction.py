import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.eval import prompt_list, model_list
from evaluation.utils import list_to_str, parse_arguments

from evaluation.r_tree.schema import ConstructionSchema, ConstructionSchemaAnsOnly


def main():

    args = parse_arguments()
    args.type = "r_tree"
    args.operation = "construction"

    i = 0
    Q_list = []

    post_truths = []
    
    with open(f"generation/r_tree/construction/rt_construction_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        if args.description == "full":
            description = "Suppose you have an empty R tree and a set of rectangles in 2D space in the form of [x_min, x_max, y_min, y_max]. \n " + \
                "You should construct an R tree with a set of given rectangles by splitting the x-axis (1st axis) first, then the y_axis (2nd axis), \n" +\
                "then loop back to x-axis... \n" +\
                "Each leaf node should contain at most M rectangles. Whenever you need to round a division, always use ceil roudning. \n" +\
                "Number of leaf nodes, therefore, should be calculated as N = ceil(N / M) \n" +\
                "Number of strips S, therefore, should be calculated as S = ceil(number of leaf node) \n" +\
                "Each node's MBR should be calculated as the minimum bounding rectangle of all rectangles in that node. \n"
        else:
            description = "Suppose you have an empty R tree and a set of rectangles in 2D space in the form of [x_min, x_max, y_min, y_max]. \n " + \
                "You should construct an R tree with a set of given rectangles by splitting the x-axis (1st axis) first, then the y_axis (2nd axis), \n" +\
                "then loop back to x-axis... \n" +\
                "Each leaf node should contain at most M rectangles. Whenever you need to round a division, always use ceil roudning. \n" +\
                "Number of leaf nodes, therefore, should be calculated as N = ceil(N / M) \n" +\
                "Number of strips S, therefore, should be calculated as S = ceil(number of leaf node) \n" +\
                "Each node's MBR should be calculated as the minimum bounding rectangle of all rectangles in that node. \n"
        Q_state = description
        
        while i < len(lines):
            
            if "M" in lines[i]:
                M = lines[i].split(" ")[-1]
                print(f"M: {M}")
                Q = f"Construct a R-tree with the following parameters: M = {M}\n"
                i += 1
            elif "Points" in lines[i]:
                recs = lines[i].split(":")[1]
                Q += f"Your R-tree should be constructed usingh the following rectangles: {recs}\n"
                Q += "After that, please answer the following question:\n" + \
                    "What is the pre-order traversal of the tree? Output in a nested list like the input. \n"
                i += 1
                print(f"Q: {Q}")
                Q = translate(Q, Q_state, args)
                Q_list += [Q]
            elif "Traversal" in lines[i]:
                values = lines[i].split(":")[1].strip()
                post_truths.append(values)
                i += 1
                pass

    traverseSchema = ConstructionSchemaAnsOnly if args.prompt == "AnsOnly" else ConstructionSchema
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

    for i in range(len(post_answers)):
        if list_to_str(post_answers[i]).strip() == list_to_str(post_truths[i]).strip():
            score.append(1)
        else:
            score.append(0)
            print(repr(list_to_str(post_answers[i]).strip()))
            print(repr(list_to_str(post_truths[i]).strip()))
            
            
 
    log(Q_list, score, answers, args)

if __name__ == "__main__":
    main()
