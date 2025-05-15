import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.eval import prompt_list, model_list
from evaluation.utils import list_to_str

from evaluation.binary_tree.schema import TraverseSchema, TraverseSchemaAnsOnly


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default="gpt-4o-mini", help='name of LM (default: gpt-4o-turbo)', choices=model_list)
    parser.add_argument('--mode', type=str, default="easy", help='mode (default: easy)')
    parser.add_argument('--prompt', type=str, default="none", help='prompting techniques (default: none)', choices=prompt_list)
    parser.add_argument('--T', type=float, default=0, help='temprature (default: 0)')
    parser.add_argument('--token', type=int, default=1500, help='max token (default: 400)')
    parser.add_argument('--batch', type=bool, default=False, help='batch eval if True (default: False)')
    parser.add_argument('--format', type=str, default="schema", help='type of structured format method, schema or function (default: schema)')
    args = parser.parse_args()
    args.type = "binary_tree"
    args.operation = "traversal"


    i = 0
    Q_list = []
    with open(f"generation/binary_tree/bt_generation/array_input_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            if i < len(lines) and "Tree" in lines[i]:
                root = None
                Q_state = "You should create a binary tree. "
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
            Q += "\nPlease answer the following questions. \n" \
                + "1. What is the pre-order traversal of the tree? \n "  \
                + "2. What is the in-order traversal of the tree? \n  "  \
                + "3. What is the post-order traversal of the tree? \n  "  \
                + "4. What is the depth of the tree? \n  "  \
                + """For questions 1 to 3, your answer should only include a list of numbers in "[" and "]", where the numbers indicating the Node index are separated by ",".  \n """ \
                + "For question 4, your answer should be only an integer. \n  " \
                # + "Final answers to all questions should be wrapped by a single '<answer>' and '</answer>' tag. \n"

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

    pre_answers = []
    in_answers = []
    post_answers = []
    depth_answers = []

    for answer in answers:
        try:
            js_answer = json.loads(answer)
        except Exception as e:
            print(f"Error encountered probably due to short of tokens.")
            pre_answers.append("")
            post_answers.append("")
            in_answers.append("")
            depth_answers.append("-1")
            continue 

        pre_answers.append(js_answer["final_answer"]["pre_order"])
        in_answers.append(js_answer["final_answer"]["in_order"])
        post_answers.append(js_answer["final_answer"]["post_order"])
        depth_answers.append(js_answer["final_answer"]["depth"])

    pre_truths = []
    in_truths = []
    post_truths = []
    depth_truths = []

    with open(f"generation/binary_tree/traversal/traversal_{args.mode}.txt", "r") as f:
        for line in f:
            if "Pre" in line:
                nums = line[line.index(":")+2:-1]
                while nums[-1] == " ":
                    nums = nums[:-1]
                nums = nums.replace(" ", ",")
                nums = "[" + nums + "]"
                pre_truths.append(nums)
            elif "In" in line:
                nums = line[line.index(":") + 2:-1]
                while nums[-1] == " ":
                    nums = nums[:-1]
                nums = nums.replace(" ", ",")
                nums = "[" + nums + "]"
                in_truths.append(nums)
            elif "Post" in line:
                nums = line[line.index(":") + 2:-1]
                while nums[-1] == " ":
                    nums = nums[:-1]
                nums = nums.replace(" ", ",")
                nums = "[" + nums + "]"
                post_truths.append(nums)
            elif "Depth" in line:
                depth = line[line.index(":") + 2:-1]
                depth_truths.append(depth)

    if len(in_answers) < len(pre_answers):
        in_answers.append("")
    if len(post_answers) < len(pre_answers):
        post_answers.append("")
    if len(depth_answers) < len(pre_answers):
        depth_answers.append("-1")

    score_pre = []
    score_in = []
    score_post = []
    score_depth = []

    for i in range(len(pre_answers)):
        if str(pre_answers[i]) == pre_truths[i]:
            score_pre.append(1)
        else:
            score_pre.append(0)
            print(pre_answers[i], pre_truths[i])
        if str(in_answers[i]) == in_truths[i]:
            score_in.append(1)
        else:
            score_in.append(0)
        if list_to_str(post_answers[i]) == post_truths[i]:
            score_post.append(1)
        else:
            score_post.append(0)
        if int(depth_answers[i]) == int(depth_truths[i]):
            score_depth.append(1)
        else:
            score_depth.append(0)

    args.operation = "preorder"
    log(Q_list, score_pre, answers, args)
    args.operation = "inorder"
    log(Q_list, score_in, answers, args)
    args.operation = "postorder"
    log(Q_list, score_post, answers, args)
    args.operation = "depth"
    log(Q_list, score_depth, answers, args)


if __name__ == "__main__":
    main()

