import openai
import os
import argparse
import json
import ast

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

from evaluation.skip_list.schema import SkipListSchema, SkipListSchemaAnsOnly


def main():
    args = parse_arguments()
    args.type = "skip_list"
    args.operation = "compound"

    truths = []
    i = 0
    Q_list = []
    with open(f"generation/skip_list/compound/compound_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            # Skip any empty lines
            if not lines[i].strip():
                i += 1
                continue

            # Expect a header line of the form:
            # "SkipList 0 (Max Level: 3)"
            header_line = lines[i].strip()
            # Parse the max_level from the header
            try:
                # header_line.split("Max Level:") returns something like ["SkipList 0 (", "3)"]
                max_level_str = header_line.split("Max Level:")[1].strip(" )")
                max_level = int(max_level_str)
            except Exception as e:
                print(f"Error parsing max level from header: {header_line}")
                max_level = None

            if args.description == "full":
                description = (
                    "A skip list is a probabilistic data structure with multiple levels. \n"
                    "The bottom layer is a standard sorted linked list. \n"
                    "Each higher layer skips over more elements, allowing fast traversal. \n"
                    "It has two operations: , and (delete, value) which deletes the value. \n"
                    "1. (insert, value) which inserts a value by \n"
                        "a) Perform a search to find the position where the new value should go. \n"
                        "b) Insert the new value to the bottom layer. \n"
                        "c) Generate a random probability to decide whether to promote the node to the next level. \n"
                        "d) Repeat step c until you stop or reach the maximum level. \n"
                    "2. (delete, value) which deletes the value by \n"
                        "a) Search for the node at the top-most level. \n"
                        "b) At each level where the node exists, remove the pointer to that node. \n"
                        "c) Continue moving downward and remove the node at all lower levels. \n"
                )
            else:
                description = (
                    "A skip list has two operations: \n"
                    "(insert, value) which inserts a value to a random number of levels, and (delete, value) which deletes the value. \n"
                )

            # Build Q with a skip list description including level generation probabilities.
            Q_state = description + (
                "For each insert operation, use the level generation probabilities provided. \n"
                    "If a probability is below 0.5 and the maximum level has not been reached, \n"
                    "the node is promoted to the next level. \n"
                "The final state of the skip list should be represented as a list of lists, \n"
                "where each inner list corresponds to one level (from the highest level to level 0). \n"
                "Empty levels should not be included in the final output. \n"
            )
            Q = f"Q: You are given an empty skip list with max level {max_level}, what is the final state of the skip list after the following operations? \n"

            # Move to the next line (operations start)
            i += 1

            # Process operation lines until we hit a line starting with '[' (the final state)
            while i < len(lines) and not lines[i].strip().startswith('['):
                line = lines[i].strip()
                # Include every line, including the level generation probabilities.
                Q += line + "\n"
                i += 1

            # The line starting with '[' should be the final skip list state (ground truth)
            if i < len(lines):
                truth_line = lines[i].strip()
                truths.append(truth_line)
            else:
                truths.append("")
            # Optionally, translate Q using Q_state
            
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": [[35, 61, 43, 83], [56, 24, 64, 92, 32]] \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": [[35, 61, 43, 83], [56, 24, 64, 92, 32]] \n' +\
                                '}\n '
            Q = translate(Q, Q_state, args)
            Q_list.append(Q)
            i += 1  # Move past the final state line
            # Skip any blank line after a test case
            if i < len(lines) and not lines[i].strip():
                i += 1

    skipListSchema = SkipListSchemaAnsOnly if args.prompt == "AnsOnly" else SkipListSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, skipListSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, skipListSchema)
        else:
            raise Exception("Invalid format type.")

    res = []
    partial_res = []
    for i in range(len(answers)):
        try:
            js_answer = json.loads(answers[i])
        except Exception as e:
            print(f"Error encountered in answer {i}: {e}")
            res.append(0)
            partial_res.append(0)
            continue 
        answer = js_answer["final_answer"]
        if str(answer) == str(truths[i]):
            res.append(1)
        else:
            res.append(0)
        partial_res.append(1 - levenshtein(str(answer), str(truths[i])))

    log(Q_list, res, partial_res, answers, args)


if __name__ == "__main__":
    main()
