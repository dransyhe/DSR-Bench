import openai
import os
import argparse
import json
import ast

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

# Assuming you have a schema for trie tree evaluation.
from evaluation.trie.schema import TrieSchema, TrieSchemaAnsOnly

def main():
    args = parse_arguments()
    args.type = "trie"
    args.operation = "compound"

    truths = []
    i = 0
    Q_list = []
    with open(f"generation/trie/compound/compound_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            # Skip empty lines.
            if not lines[i].strip():
                i += 1
                continue

            if args.description == "full":
                description = (
                    "A trie tree is a data structure that stores strings by sharing common prefixes with the following properties: \n"
                    "Each node represents a character. \n"
                    "The path from the root to a node spells out a prefix. \n"
                    "It has two operations: \n"
                    "1. (insert, word) which inserts a word by \n"
                        "a) Starting from the root node. \n"
                        "b) For each character in the word, check if it exists in the current node's children. \n"
                        "c) If it exists, move to that child node. \n"
                        "d) If it doesn't exist, create a new child node for that character and move to it. \n"
                        "e) Repeat until all characters in the word are processed. \n"
                    "2. (delete, word) which deletes a word by \n"
                        "a) Traverse down the trie tree following the word’s characters. \n"
                        "b) Once the leaf node is reached, delete from bottom-up if a node has no children or is not part of another word. \n"
                )
            else:
                description = (
                    "A trie tree has two operations: \n"
                    "1. (insert, word) which inserts a word to the trie tree to the appropriate position. \n"
                    "2. (delete, word) which removes a word from the trie tree. \n"
                )
            Q_state = description + (
                "After all operations, the final state of the trie is represented as the pre-order traversal of the trie tree (i.e. a list of characters), \n"
                "where children are visited in sorted order of their characters. \n"
                "The root node is represented as an empty string. \n"
            )
            
            # Header line, e.g., "TrieTree 0".
            header_line = lines[i].strip()
            Q = "Q: You are given an empty trie tree, what is its final state after the following operations? \n"
            i += 1

            # Append all operation lines until reaching the final state line (starting with '[').
            while i < len(lines) and not lines[i].strip().startswith('['):
                line = lines[i].strip()
                Q += line + "\n"
                i += 1

            # The final state line (starting with '[') is the ground-truth pre-order traversal.
            if i < len(lines):
                truth_line = lines[i].strip()
                truths.append(truth_line)
            else:
                truths.append("")
                
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": ["t", "w", "d", "h", "s", "b", "x"] \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": ["t", "w", "d", "h", "s", "b", "x"]  \n' +\
                                '}\n '
            
            Q = translate(Q, Q_state, args)
            Q_list.append(Q)
            i += 1  # Move past the final state line.
            if i < len(lines) and not lines[i].strip():
                i += 1

    trieSchema = TrieSchemaAnsOnly if args.prompt == "AnsOnly" else TrieSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, trieSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, trieSchema)
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
