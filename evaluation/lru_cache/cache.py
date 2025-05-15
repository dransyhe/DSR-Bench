import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.eval import prompt_list, model_list
from evaluation.utils import str_to_int_list, parse_arguments, levenshtein

from evaluation.lru_cache.schema import LruCacheSchema, LruCacheSchemaAnsOnly  # Assumed schema definitions


def main():
    args = parse_arguments()
    args.type = "lru_cache"
    args.operation = "cache"

    truths = []
    Q_list = []

    # Open the file for the corresponding mode, e.g., "lru_easy.txt"
    with open(f"generation/lru_cache/cache/lru_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            if "Simulation" in lines[i]:
                cache_size = lines[i].split(":")[1].strip()
                Q = "You should create a LRU cache with cache size (max number of different pages stored in cache) " + cache_size + ".\n"
                i += 1 

            # The state prompt describing the LRU cache operations
            if args.description == "full":
                Q_state = (
                    "An LRU (Least Recently Used) cache is a fix-sized array-based data structure. \n"
                    "It supports a single operation: (access, p) where 'p' is a page number. \n"
                    "When a page is accessed, if it is already in the cache, it is moved to the most recently used position. \n"
                    "If the page is not in the cache, and the cache is not full, the page is added. \n"
                    "If the cache is full and the page is not present, the least recently used page is evicted to insert the new page. \n"
                )
            else:
                Q_state = (
                    "A fix-sized LRU (Least Recently Used) cache supports a single operation: (access, p) where 'p' is a page number, \n"
                    "which means page p is accessed. \n"
                )

            Q += "Q: Initially, the cache is empty. What is the state of the LRU cache after the following sequence of operations:\n"
            
            # Process each operation until a final state (starting with '[') is encountered.
            while i < len(lines) and "[" not in lines[i]:
                if "access" in lines[i]:
                    # Extract the page number from a line like "access 7"
                    num = int(lines[i].split(" ")[-1])
                    Q += f"(access, {num})\n"
                    i += 1
                    
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": [56, 23, 78] \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": [56, 23, 78] \n' +\
                                '}\n '
                    
            # Translate the natural language query if needed
            Q = translate(Q, Q_state, args)

            if "Final" in lines[i]:
                truths.append(lines[i].split(":")[1].strip())
                i += 1
                
            Q_list.append(Q)

    # Choose the appropriate schema based on the prompt technique
    lruSchema = LruCacheSchemaAnsOnly if args.prompt == "AnsOnly" else LruCacheSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, lruSchema)
    else:
        if args.format == "schema":
            answers = predict(Q_list, args, lruSchema)
        else:
            raise Exception("Invalid format type.")

    res = []
    partial_res = []
    for i in range(len(answers)):
        try:
            js_answer = json.loads(answers[i])
            answer = js_answer["final_answer"]
        except Exception as e:
            print(f"Error encountered: {e}")
            res.append(0)
            partial_res.append(0)
            continue 
        if set(str_to_int_list(answer)) == set(str_to_int_list(truths[i])):
            res.append(1)
        else:
            res.append(0)
            print(set(str_to_int_list(answer)))
            print(set(str_to_int_list(truths[i])))
        edit_dist = levenshtein(str(set(str_to_int_list(answer))), str(set(str_to_int_list(answer))))
        partial_res.append(1 - edit_dist)

    log(Q_list, res, partial_res, answers, args)


if __name__ == "__main__":
    main()
