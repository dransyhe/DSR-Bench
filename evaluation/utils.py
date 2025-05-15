import argparse
import json
import re
import ast
from typing import List
from tiktoken import encoding_for_model, get_encoding

from evaluation.eval import prompt_list, model_list

def list_to_str(l):
    return str(l).replace(" ", "")

def str_to_int_list(s):
    if type(s) == list:
        return [int(i) for i in s]
    s = s.replace(" ", "")
    s = s.replace("[", "").replace("]", "")
    return [int(i) for i in s.split(",")]

def str_to_nested_float_list(s):
    try:
        parsed = ast.literal_eval(s)       
    except (SyntaxError, ValueError) as exc:
        raise ValueError(f"Input is not a valid list literal: {exc}")

    if not (isinstance(parsed, list) and all(isinstance(row, list) for row in parsed)):
        raise ValueError("Parsed object is not a list of lists.")

    try:
        return [[float(x) for x in row] for row in parsed]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Could not convert all elements to float: {exc}")

def count_num_tokens(text):
    tokenizer = get_encoding("cl100k_base")
    return len(tokenizer.encode(text))

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default="gpt-4o-mini", help='name of LM (default: gpt-4o-turbo)', choices=model_list)
    parser.add_argument('--mode', type=str, default="easy", help='mode (default: easy)')
    parser.add_argument('--description', type=str, default="full", help='whether to use full description or name-dropping', choices=["full", "name"])
    parser.add_argument('--prompt', type=str, default="none", help='prompting techniques (default: none)', choices=prompt_list)
    parser.add_argument('--T', type=float, default=0, help='temprature (default: 0)')
    parser.add_argument('--token', type=int, default=1500, help='max token (default: 400)')
    parser.add_argument('--batch', type=bool, default=False, help='batch eval if True (default: False)')
    parser.add_argument('--format', type=str, default="schema", help='type of structured format method, schema or function (default: schema)')
    parser.add_argument('--dim', type=int, default=5, help='dimension for kd-heap, kd-tree, and geometric graph')
    args = parser.parse_args()
    return args 

def _levenshteinRecursive(str1, str2, m, n):
    if m == 0:
        return n
    if n == 0:
        return m
    if str1[m - 1] == str2[n - 1]:
        return _levenshteinRecursive(str1, str2, m - 1, n - 1)
    return 1 + min(_levenshteinRecursive(str1, str2, m, n - 1),
        min(_levenshteinRecursive(str1, str2, m - 1, n),
            _levenshteinRecursive(str1, str2, m - 1, n - 1)))
    
def levenshtein2(str1, str2):
    """
    Archived distance function because it cannot handle recursion over large strings
    """
    m = len(str1)
    n = len(str2)
    return _levenshteinRecursive(str1, str2, m, n) / max(m, n)


def levenshtein(a: str, b: str, normalise: bool = True) -> float | int:
    m, n = len(a), len(b)
    if m == 0 or n == 0:
        dist = m + n            # one is zero
        return dist / max(m, n) if normalise and max(m, n) else 0

    # Two-row DP saves memory
    prev = list(range(n + 1))
    cur  = [0]*(n + 1)

    for i in range(1, m + 1):
        cur[0] = i
        for j in range(1, n + 1):
            cost = 0 if a[i-1] == b[j-1] else 1
            cur[j] = min(
                prev[j]   + 1,      # delete
                cur[j-1]  + 1,      # insert
                prev[j-1] + cost    # substitute
            )
        prev, cur = cur, prev       # swap; reuse lists

    dist = prev[n]
    return dist / max(m, n) if normalise else dist



if __name__ == "__main__":
    # print(levenshtein2('[80,26,19,69,42,71,91]', '[91,26,19,80,69,42,71]'))
    
    print(str_to_nested_float_list([[63.7,26.98],[81.59,0.27],[85.74,3.36]]))
    print(type(str_to_nested_float_list(' [[63.7, 26.98], [81.59, 0.27], [85.74, 3.36]]')))