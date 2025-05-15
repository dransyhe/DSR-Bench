import openai
import os
import argparse
import json
import ast

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

# Assuming you have a schema for DAWG evaluation.
from evaluation.dawg.schema import DAWGSchema, DAWGSchemaAnsOnly

def main():
    args = parse_arguments()
    args.type = "dawg"
    args.operation = "compound"

    truths = []
    i = 0
    Q_list = []
    with open(f"generation/dawg/compound/compound_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            if not lines[i].strip():
                i += 1
                continue

            # Expect a header line like "DAWG 0 (Mode: easy)".
            header_line = lines[i].strip()
            
            if args.description == "full":
                description = (
                    "A Directed Acyclic Word Graph (DAWG) encodes a set of lowercase words (a-z) as a compressed trie in a directed acyclic graph.\n"
                    "Each node has an is_end flag ('T' for true, and 'F' for false) indicating whether the path from the root to that node spells a complete word.\n"
                    "Each edge carries a single-character label, extending prefixes by one letter.\n"
                    "Starting from an empty DAWG, apply a sequence of operations of two types:\n"
                    "1. insert(word):\n"
                    "   a) Begin at the root node.\n"
                    "   b) For each character c in word:\n"
                    "      - If no c-labeled edge exists, create a new child node (is_end='F') and attach it.\n"
                    "      - Move along the c-edge to that child node.\n"
                    "   c) After the final character, set is_end='T' on the current node to mark a complete word.\n"
                    "2. delete(word):\n"
                    "   a) Begin at the root and follow each character's edge to the terminal node of word.\n"
                    "   b) Set is_end='F' on that terminal node so it's no longer recognized as a word.\n"
                    "   c) As you backtrack toward the root, at each node:\n"
                    "      - If the node has no children and is_end is 'F', remove it from its parent's children.\n"
                    "After all operations, you should minimize the DAWG by merging identical suffix-subtrees:\n"
                    "   a) Recursively process every node from the leaves up.\n"
                    "   b) At each node, compute a signature:\n"
                    "        (node.is_end, sorted list of (char, child.signature) for each child)\n"
                    "   c) Use a registry mapping signatures to nodes:\n"
                    "        - If a node's signature exists, replace it with the registered node.\n"
                    "        - Otherwise, register this node under its signature.\n"
                    "   d) After this pass, all identical suffix-subtrees share a single node, yielding the minimal DAWG.\n"
                )
            else:
                description = (
                    "A Directed Acyclic Word Graph (DAWG) encodes a set of lowercase words (a-z) as a compressed trie in a directed acyclic graph.\n"
                    "Each node has an is_end flag ('T' for true, and 'F' for false) indicating whether the path from the root to that node spells a complete word.\n"
                    "Each edge carries a single-character label, extending prefixes by one letter.\n"
                    "Starting from an empty DAWG, apply a sequence of operations of two types:\n"
                    "1. (insert, word) adds a word by creating nodes and edges as needed.\n"
                    "2. (delete, word) removes a previously inserted word and update the nodes.\n"
                    "After all operations, you should minimize the DAWG by merging nodes merge any two nodes whose suffix-subtrees are identical, \n"
                    "which means their subgraphs (their is_end flag plus all outgoing edges and downstream structure) are identical.\n"
                )

            Q_state = description + (
                "To export the final DAWG, perform a breadth-first traversal from the root and record each node as \n"
                "(prefix, is_end), where prefix is the string formed by following edges from the root. \n"
                "The prefix for the root node is an empty string. \n"
                "Outgoing edges are visited in ascending lexicographical order. \n"
            )
            
            # TODO: need to update this after DAWG output format is updated
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '''    "final_answer": [['', 'F'], ['d', 'F'], ['g', 'F'], ['da', 'F'], ['dz', 'F'], ['dar', 'T'], ['dzs', 'F']]\n''' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '''    "final_answer": [['', 'F'], ['d', 'F'], ['g', 'F'], ['da', 'F'], ['dz', 'F'], ['dar', 'T'], ['dzs', 'F']]\n''' +\
                                '}\n '
            
            Q = "Q: You are given an empty Directed Acyclic Word Graph (DAWG), what is its final state after the following operations?\n"
            i += 1

            # Append all operation lines until reaching a line starting with '[' (the final state).
            while i < len(lines) and not lines[i].strip().startswith('['):
                line = lines[i].strip()
                Q += line + "\n"
                i += 1

            # The line starting with '[' is the ground-truth final state (nested list from pre-order traversal).
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

    dawgSchema = DAWGSchemaAnsOnly if args.prompt == "AnsOnly" else DAWGSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, dawgSchema)
    else:
        if args.format == "schema":
            answers = predict(Q_list, args, dawgSchema)
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
        answer = str(answer).replace('"', "'")
        if str(answer) == str(truths[i]):
            res.append(1)
        else:
            print(f"Wrong at index {i}")
            print(f"Answer: {answer}")
            print(f"Truth: {truths[i]}")
            res.append(0)
        partial_res.append(1 - levenshtein(str(answer), str(truths[i])))

    log(Q_list, res, partial_res, answers, args)

if __name__ == "__main__":
    main()
