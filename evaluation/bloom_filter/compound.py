import openai
import os
import argparse
import json
import ast

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

from evaluation.bloom_filter.schema import BloomFilterSchema, BloomFilterSchemaAnsOnly

def main():
    args = parse_arguments()
    args.type = "bloom_filter"
    args.operation = "compound"

    truths = []
    i = 0
    Q_list = []
    with open(f"generation/bloom_filter/compound/compound_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            if not lines[i].strip():
                i += 1
                continue

            # Expect header like "BloomFilter 0 (m: 20, k: 3)"
            header_line = lines[i].strip()
            try:
                parts = header_line.split("m:")
                m_part = parts[1].split(",")[0].strip()
                m_val = int(m_part)
                k_part = parts[1].split("k:")[1].strip(" )")
                k_val = int(k_part)
            except Exception as e:
                print(f"Error parsing parameters from header: {header_line}")
                m_val, k_val = None, None

            if args.description == "full":
                description = (
                    "A Counting Bloom Filter is a probabilistic data structure used for set membership queries, with the added ability to delete elements. \n"
                    "It maintains an array of counters of size m and uses k independent hash functions. "
                    "It supports two operations: \n"
                    "1. (insert v): To insert an element v, each hash function determines a position in the count array and increments the counter at that position; \n"
                    "2. (delete v): To delete an element v, each corresponding counter is decremented (ensuring that counters never drop below zero). \n"
                )
            else:
                description = (
                    "A Counting Bloom Filter maintains an array of counters of size m and uses k independent hash functions. \n"
                    "It supports two operations: \n"
                    "1. (insert v): Insert an element v using the hash function and update the counter. \n"
                    "2. (delete v): Delete an element v and update the counter. \n"
                )
            Q_state = description + (
                "You should use a custom hash function described as:\n"
                "a) Convert the input item to a string.\n"
                "b) Initialize a hash accumulator to 0.\n"
                "c) For each character in the string, update the accumulator as: h = h * 131 + ord(character).\n"
                "d) Add a given salt value to the accumulator.\n"
                "e) Finally, compute the result as h modulo m (the size of the count array).\n"
                "For each item and a salt with value i (defined as the i-th hash function, where i=0, ..., (k-1)), \n"
                "this computation deterministically produces an index in the range [0, m-1].\n"
            )
            Q = (f"Q: You are given an empty Counting Bloom Filter with m = {m_val} and k = {k_val}.\n"
                  "What is the final state of the Counting Bloom Filter, represented as its count array (a list of integer counts), after the following operations? \n"
            )
            i += 1

            # Append all operation lines until reaching a line starting with '[' (the final state).
            while i < len(lines) and not lines[i].strip().startswith('['):
                line = lines[i].strip()
                Q += line + "\n"
                i += 1

            if i < len(lines):
                truth_line = lines[i].strip()
                truths.append(truth_line)
            else:
                truths.append("")
                
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": [0, 0, 0, 0, 1, 1] \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": [0, 0, 0, 0, 1, 1] \ \n' +\
                                '}\n '    
            
            Q = translate(Q, Q_state, args)
            Q_list.append(Q)
            i += 1  # Move past the final state line.
            if i < len(lines) and not lines[i].strip():
                i += 1

    bloomFilterSchema = BloomFilterSchemaAnsOnly if args.prompt == "AnsOnly" else BloomFilterSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, bloomFilterSchema)
    else:
        if args.format == "schema":
            answers = predict(Q_list, args, bloomFilterSchema)
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
