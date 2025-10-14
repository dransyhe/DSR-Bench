import openai
import os
import argparse
import json
import ast

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

# Assuming you have a schema for suffix tree evaluation.
from evaluation.suffix_tree.schema import SuffixTreeSchema, SuffixTreeSchemaAnsOnly

def main():
    args = parse_arguments()
    args.type = "suffix_tree"
    args.operation = "construct"

    truths = []
    Q_list = []
    i = 0

    with open(f"generation/suffix_tree/construct/construct_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            if not lines[i].strip():
                i += 1
                continue

            # Read header line (e.g., "SuffixTree 0")
            header_line = lines[i].strip()
            i += 1

            # Read the word line.
            if i >= len(lines):
                break
            word_line = lines[i].strip()
            i += 1

            # Read the ground truth line (expected to start with '[')
            if i >= len(lines):
                break
            truth_line = lines[i].strip()
            truths.append(truth_line)
            i += 1

            if args.description == "full":
                description = (
                    "A suffix tree is a data structure that compactly represents all suffixes of a given string. \n"
                    "It has the following properties: \n"
                    "Given a string s of length n, there are n suffixes. \n"
                    "Each path from the root to a leaf spells out a suffix of s. \n" 
                    "Edges are labeled with substrings. \n"
                    "Internal nodes represent shared prefixes among suffixes. \n"
                    "Leaves are labeled with the starting index of the suffix. \n"
                )
            else:
                description = (
                    ""
                )

            # Build the prompt using the word from the file.
            Q_state = description + (
                "The required output is the pre-order traversal of this suffix tree, collecting the edge labels encountered along the way. \n"
                "When performing the traversal, ensure that at each node the child edges are visited in lexicographical order, \n"
                "with the '$' edge prioritized to be visited before any other character. \n"
                "The final output should be a list that represents the flattened sequence of edge labels. "
            )
            Q = f"Q: Given a word {word_line}, what does its suffix tree look like?\n"
            
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": ["$", "gok$", "k$", "ok$", "y", "gok$", "ygok$"] \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": ["$", "gok$", "k$", "ok$", "y", "gok$", "ygok$"] \n' +\
                                '}\n '
                                
            Q = translate(Q, Q_state, args)
            Q_list.append(Q)

            # Skip any extra blank lines between entries.
            while i < len(lines) and not lines[i].strip():
                i += 1

    suffixTreeSchema = SuffixTreeSchemaAnsOnly if args.prompt == "AnsOnly" else SuffixTreeSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, suffixTreeSchema)
    else:
        if args.format == "schema":
            answers = predict(Q_list, args, suffixTreeSchema)
        else:
            raise Exception("Invalid format type.")

    res = []
    partial_res = []
    for idx, ans in enumerate(answers):
        try:
            js_answer = json.loads(ans)
        except Exception as e:
            print(f"Error encountered in answer {idx}: {e}")
            res.append(0)
            partial_res.append(0)
            continue
        answer = js_answer["final_answer"]
        if str(answer) == str(truths[idx]):
            res.append(1)
        else:
            res.append(0)
        partial_res.append(1 - levenshtein(str(answer), str(truths[idx])))

    log(Q_list, res, partial_res, answers, args)

if __name__ == "__main__":
    main()
