import openai
import os
import argparse
import json
import ast

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

from evaluation.hashmap.schema import HashMapSchema, HashMapSchemaAnsOnly

import json

def answer_to_hashmap(answer):
    """
    Extract JSON formatted LLM answer to a nested Python list of (int, int) tuples,
    sorting the entries in ascending order by the "number" field.
    """
    data = json.loads(answer)
    final_ans = data["final_answer"]
    
    # Sort the list of buckets by the "number" key in ascending order.
    final_ans = sorted(final_ans, key=lambda bucket: bucket["number"])

    converted_buckets = []
    for bucket in final_ans:
        tuple_list = []
        for pairs in bucket["contents"]:
            tuple_list.append((pairs["key"], pairs["value"]))
        converted_buckets.append(tuple_list)
        
    return converted_buckets


def truth_to_hashmap(s):
    """
    Convert a string representation of a list of list of tuples to a list of tuples.
    """
    hashmap_str = s.split(":", 1)[1].strip()
    hashmap_list = ast.literal_eval(hashmap_str)
    return hashmap_list

def main():

    args = parse_arguments()
    args.type = "hashmap"
    args.operation = "compound"


    truths = []

    i = 0
    Q_list = []
    with open(f"generation/hashmap/compound/compound_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):

            if args.description == "full":
                description = "A hashmap is a dictionary that stores key-value pairs. " + \
                "It has two operations: (add, (key, value)) and (delete, key).  \n" + \
                "1. (add, (key, value)) adds a (key, value) pair to the hashmap by a) mapping key to a bucket using hash function, and b) put (key, value) pair in the bucket. If key exists in the bucket already, update its value. \n " + \
                "2. (remove, key) removes the (key, value) pair by a) mapping key to the bucket using hash function, and b) find (key, value) pair in the bucket and remove it. \n" 
            else:
                description = \
                "A hashmap has two operations: (add, (key, value)) and (delete, key).  \n" + \
                "1. (add, (key, value)) adds or updates a (key, value) pair to the hashmap. \n " + \
                "2. (remove, key) removes the (key, value) pair from the hashmap. \n" 

            Q_state = description 
                
            num_buckets = int(lines[i].split(" ")[-3])
            
            Q = f"Q: You are given an empty hashmap with {num_buckets} buckets initially. The hash function you will use is bucket = key % bucket_number. Bucket number is indexed from 0 to {num_buckets - 1}. The operations are: \n"

            while i < len(lines) and "[" not in lines[i]:
                if "add" in lines[i]:
                    key = int(lines[i].split(" ")[2])
                    value = int(lines[i].split(" ")[4])
                    Q += f"(add, ({key}, {value}))\n"
                elif "remove" in lines[i]:
                    key = int(lines[i].split(" ")[1])
                    Q += f"(remove, {key})\n"
                i += 1
                
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": [{"number": 0, "contents": [{"key": 30, "value": 95}, {"key": 75, "value": 34]}] }, {"number": 1, "contents": [{"key": 71, "value": 54}] }, {"number": 2, "contents": []}] \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": [{"number": 0, "contents": [{"key": 30, "value": 95}, {"key": 75, "value": 34]}] }, {"number": 1, "contents": [{"key": 71, "value": 54}] }, {"number": 2, "contents": []}] \n' +\
                                '}\n '

            Q = translate(Q, Q_state, args)

            truths.append(truth_to_hashmap(lines[i][:-2]))
            Q_list += [Q]
            i += 2

    hashSchema = HashMapSchemaAnsOnly if args.prompt == "AnsOnly" else HashMapSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, hashSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, hashSchema)
        else:
            raise Exception("Invalid format type.")

    res = []
    partial_res = []
    log_answers = []
    
    for i, answer in enumerate(answers):
        try:
            answer = answer_to_hashmap(answer)
        except Exception as e:
            print(f"Error encountered at index {i}: {e}")
            res.append(0)
            partial_res.append(0)
            log_answers.append("")
            continue
        log_answers.append(answer)
        if answer == truths[i]:
            res.append(1)
        else:
            res.append(0)
        partial_res.append(1 - levenshtein(str(answer), str(truths[i])))

    log(Q_list, res, partial_res, answers, args)


if __name__ == "__main__":
    main()
