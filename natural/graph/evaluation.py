#!/usr/bin/env python3
import os
import random
import argparse
import ast
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments

from natural.graph.schema import GraphSchema, GraphSchemaAnsOnly

from evaluation.utils import levenshtein

def main():
    args = parse_arguments()
    args.type = "graph"
    args.operation = "natural"

    base_dir     = os.path.dirname(__file__)
    natural_path = os.path.join(base_dir, f"natural-{args.mode}.txt")
    desc_path    = os.path.join(base_dir, "template", "description.txt")
    node_path    = os.path.join(base_dir, "template", "node.txt")
    edge_path    = os.path.join(base_dir, "template", "edge.txt")

    # --- 1) read and parse each instance ---
    raw_blocks = open(natural_path).read().strip().split("\n\n")
    instances = []
    for block in raw_blocks:
        data = {}
        for line in block.splitlines():
            key, val = line.split(": ", 1)
            if key in ("nodes", "edges", "traversal"):
                data[key] = ast.literal_eval(val)
            elif key == "source":
                data[key] = val
        instances.append(data)

    # --- 2) load templates ---
    descriptions = [l.strip() for l in open(desc_path) if l.strip()]
    node_tmpls   = [l.strip() for l in open(node_path) if l.strip()]
    edge_tmpls   = [l.strip() for l in open(edge_path) if l.strip()]

    Q_list = []
    truths = []

    for inst in instances:
        nodes     = inst["nodes"]
        edges     = inst["edges"]
        source    = inst["source"]
        truth     = inst["traversal"]

        planets = set([])

        # 3) build the prompt
        desc = random.choice(descriptions)
        Q = desc + "\n\n"

        # 3a) node descriptions
        # for p in nodes:
        #     tmpl = random.choice(node_tmpls)
        #     Q += tmpl.replace("{planet}", p) + "\n"
        # Q += "\n"

        # 3b) edge descriptions
        for u, v in edges:
            tmpl = random.choice(edge_tmpls)
            Q += tmpl.replace("{planet1}", u).replace("{planet2}", v) + "\n"
            planets.add(u)
            planets.add(v)
            if "{other_planet}" in tmpl:
                candidates = list(planets - {u, v})
                other_planet = random.choice(candidates) if candidates else "some other planet"
                Q = Q.replace("{other_planet}", other_planet)
        Q += "\n"

        # 4) final question
        Q += (
            f"Q: What is the full DFS traversal order (as a list of planet names) "
            f"starting from {source}? "
        )

        Q_list.append(translate(Q, desc, args))
        truths.append(truth)

    # --- 5) get model answers ---
    schema = GraphSchemaAnsOnly if args.prompt == "AnsOnly" else GraphSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, schema)
    else:
        if args.format == "schema":
            answers = predict(Q_list, args, schema)
        else:
            raise Exception("Invalid format type.")

    # --- 6) evaluate ---
    res = []
    partial_res = []
    for idx, ans_text in enumerate(answers):
        try:
            js  = json.loads(ans_text)
            ans = js["final_answer"]
        except Exception:
            res.append(0)
            partial_res.append(0)
            continue

        # normalize to list
        if isinstance(ans, list):
            ans_list = ans
        else:
            ans_list = ast.literal_eval(ans)

        if ans_list == truths[idx]:
            res.append(1)
        else:
            res.append(0)
            print(f"Answer[{idx}]: {ans_list}")
            print(f"Truth [{idx}]: {truths[idx]}")
        partial_res.append(1 - levenshtein(str(ans_list), str(truths[idx])))

    log(Q_list, res, partial_res, answers, args)

if __name__ == "__main__":
    main()
