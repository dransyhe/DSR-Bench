import openai
import os
import argparse
import json
import ast

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

from evaluation.b_plus_tree.schema import BPlusTreeSchema, BPlusTreeSchemaAnsOnly

def main():
    args = parse_arguments()
    args.type = "b_plus_tree"
    args.operation = "compound"

    truths = []
    i = 0
    Q_list = []
    with open(f"generation/b_plus_tree/compound/compound_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            if not lines[i].strip():
                i += 1
                continue

            # Expect a header line like "BPlusTree 0 (Order: 4)"
            header_line = lines[i].strip()
            try:
                order_str = header_line.split("Order:")[1].strip(" )")
                order = int(order_str)
            except Exception as e:
                print(f"Error parsing order from header: {header_line}")
                order = None

            if args.description == "full":
                description = (
                    "In a B+ tree, internal nodes store only keys for routing while all actual data is stored in the leaf nodes. \n"
                    "There are two operations: (insert, key) to insert a key and (delete, key) to delete a key. \n"
                    "When inserting a key into a leaf, add the key and sort the keys in ascending order. If the number of keys in a leaf \n"
                    "reaches the specified order, split the leaf at its midpoint: the left leaf retains the lower half of keys, \n"
                    "and a new right leaf is created with the upper half. The smallest key from the new right leaf is promoted to the parent node. \n"
                    "For internal nodes, if an insertion causes the number of keys to reach the order, split the node at the midpoint, \n"
                    "partition its keys and children into two nodes, and promote the median key to the parent. \n"
                    "Deletion simply removes a key from the appropriate leaf without rebalancing. \n"
                )
            else: 
                description = (
                    "In a B+ tree, there are operations: (insert, key) adds a key; (delete, key) removes a key.\n"
                    "Assume internal nodes store only routing keys and all data resides in the leaves.\n"
                    "On insertion, split a node when the number of keys reaches the specified order. Promote the middle key to the parent.\n"
                    "Deletion does not trigger rebalancing or merging.\n"
                    "Assume keys are inserted into or removed from the correct position to maintain sorted order.\n"
                )
            Q_state = description
            
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": [[3, 24], [12, 14], [89], [94, 96]] \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": [[3, 24], [12, 14], [89], [94, 96]] \n' +\
                                '}\n '

            Q = ( f"Q: Given an empty B+ tree with order {order} and the following sequence of operations, what is the final state of the tree "
                "as a pre-order traversal (a list of nodes' keys), ensuring that keys in each node are sorted in ascending order? \n"
            )
            i += 1

            # Process operation lines until a line starting with '[' (final state)
            while i < len(lines) and not lines[i].strip().startswith('['):
                line = lines[i].strip()
                Q += line + "\n"
                i += 1

            if i < len(lines):
                truth_line = lines[i].strip()
                truths.append(truth_line)
            else:
                truths.append("")
            Q = translate(Q, Q_state, args)
            Q_list.append(Q)
            i += 1  # Move past the final state line.
            if i < len(lines) and not lines[i].strip():
                i += 1

    bplusTreeSchema = BPlusTreeSchemaAnsOnly if args.prompt == "AnsOnly" else BPlusTreeSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, bplusTreeSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, bplusTreeSchema)
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
