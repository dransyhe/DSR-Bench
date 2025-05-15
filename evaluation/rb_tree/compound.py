import openai
import os
import argparse
import json
import ast

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import list_to_str, parse_arguments, levenshtein

from evaluation.rb_tree.schema import RBTreeSchema, RBTreeSchemaAnsOnly

from generation.rb_tree.utils import convert_file_to_natural_language_description       


def main():

    args = parse_arguments()
    args.type = "rb_tree"
    args.operation = "compound"

    i = 0
    c = 0
    Q_list = []
    
    nl_descs = convert_file_to_natural_language_description(f"generation/rb_tree/rbt_input_{args.mode}.txt")

    truths = []
    
    with open(f"generation/rb_tree/compound/rbt_compound_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        if args.description == "full":
            description = "A red-black tree is a self-balancing binary search tree. \n" + \
                "It has the following properties: \n" + \
                "1. Each node is either red or black. \n" + \
                "2. The root is always black. \n" + \
                "3. All leaves (NIL nodes) are black. \n" + \
                "4. Red nodes cannot have red children. \n" + \
                "5. Every path from a node to its descendant NIL nodes has the same number of black nodes. \n" + \
                "It supports two main operations: \n" + \
                "1. (insert, k) inserts a key k while maintaining balance and red-black properties. \n" + \
                "   a. Insert the new node as in a regular binary search tree and color it red. \n" + \
                "   b. If the parent is black, no fix is needed. \n" + \
                "   c. If the parent is red, fix violations by performing one or more of the following: \n" + \
                "      - Recoloring: If the uncle is red, recolor the parent and uncle black, and grandparent red. \n" + \
                "      - Rotation: If the uncle is black, perform left or right rotations depending on the case (zig-zig or zig-zag). \n" + \
                "   d. Repeat the fix-up process until all properties are restored, then recolor the root black. \n" + \
                "2. (delete, k) removes a key k while preserving red-black properties. \n" + \
                "   a. Perform standard BST deletion: replace the node with its successor if it has two children. \n" + \
                "   b. If the deleted node or its replacement is red, simply remove it (no violation). \n" + \
                "   c. If a black node is removed and replaced with a black child (or NIL), fix the 'double black' violation by: \n" + \
                "      - Recoloring the sibling or its children. \n" + \
                "      - Performing left or right rotations to move the black up the tree. \n" + \
                "   d. Continue adjustments until all red-black properties are restored. \n"
        else: 
            description = "A red-black tree has two operations while maintaining the red-black properties: " + \
                "1. (insert, k) inserts a key k to the tree to the appropriate position. \n" + \
                "2. (delete, k) removes a key k from the tree to the appropriate position. \n" 

        Q_state = description + \
            "Start with an empty red-black tree, perform the provided series of" + \
            "operations on the tree. \n"
        
        while i < len(lines):
            c += 1

            Q = ""
            
            while i < len(lines) and "[" not in lines[i]:
                if "Insert" in lines[i]:
                    value = int(lines[i].split(" ")[1])
                    Q += f"Insert {value}\n"
                elif "Delete" in lines[i]:
                    value = int(lines[i].split(" ")[1])
                    Q += f"Delete {value}\n "
                i += 1

            Q += (
                "The final state of the red-black tree should be a list of (value, color) pairs from \n"
                "pre-order traversal of the tree, where color is either 0 (if 'r'), 1 (if 'b').\n"
                "Q: What is the final state of the red-black tree after performing the operations? \n" 
            )
            
            while i < len(lines) and "[" in lines[i]:
                if "Pre-order" in lines[i]:
                    values = lines[i][lines[i].index(":") + 2:]
                    values = ast.literal_eval(values)
                    color_map = {'r': 0, 'b': 1}
                    converted = [[v, color_map[c]] for v, c in values]
                    truths.append(converted)
                i += 1
                
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": [[56, 0], [67, 0], [78, 0]] \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": [[56, 0], [67, 0], [78, 0]] \n' +\
                                '}\n '
            
            Q = translate(Q, Q_state, args)
            
            Q_list += [Q]

    traverseSchema = RBTreeSchemaAnsOnly if args.prompt == "AnsOnly" else RBTreeSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, traverseSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, traverseSchema)
        else:
            raise Exception("Invalid format type.")
        
    pre_answers = []
    for answer in answers:
        try:
            js_answer = json.loads(answer)
            pre_answers.append(js_answer["final_answer"])
        except Exception as e:
            print(f"Error encountered probably due to short of tokens.")
            pre_answers.append("")
            continue
        
    score = []
    partial_score = []

    for i in range(len(pre_answers)):
        if str(pre_answers[i]) == str(truths[i]):
            score.append(1)
        else:
            score.append(0)
            print(list_to_str(pre_answers[i]).strip())
            print(list_to_str(truths[i]).strip())
        partial_score.append(1 - levenshtein(str(pre_answers[i]).strip(), str(truths[i]).strip()))

    log(Q_list, score, partial_score, answers, args)

if __name__ == "__main__":
    main()
