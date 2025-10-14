import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

from evaluation.graph.schema import GraphSchema, GraphSchemaAnsOnly


def main():

    args = parse_arguments()
    args.type = "graph"
    args.operation = "dfs"
    
    i = 0
    j = 0
    Q_list = []
    truths = []
    with open(f"generation/graph/graph_input_{args.mode}.txt", "r") as f1, open(f"generation/graph/dfs/dfs_{args.mode}.txt", "r") as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
        while i < len(lines1) and j < len(lines2):
            if args.description == "full":
                description = ("A graph consists of some nodes and edges. Each edge connects two nodes. \n" 
                "Depth-first search traverses the graph from a source node, and explores as far as possible until there is no unvisited neighbors before backtracking. \n")
            else:
                description = ""

            Q_state = description + "You should perform depth-first search on a graph. \n" + \
                "If there are multiple neighbors to explore for a given node, prioritize the neighbors with the smallest value. \n"

            # Get the graph
            i += 1
            edge_list = [] 
            while i < len(lines1) and "Graph" not in lines1[i]:
                if ", " not in lines1[i]: 
                    node_list = lines1[i].rstrip("\n") 
                else:
                    edges = lines1[i].split(", ")
                    edge_list += [(int(edges[0]), int(edges[1]))]
                i += 1

            # Get the source node 
            if "Source" in lines2[j]:
                source = int(lines2[j].split(" = ")[-1])

            edge_list = [f"({u}, {v})" for u, v in edge_list]
            edge_list = "[" + ", ".join(edge_list) + "]"
            node_list = "[" + ", ".join(node_list.split(" ")) + "]"
            Q = f"Q: The graph consists of nodes {node_list}, and edges {edge_list}. \n What is the depth-first search path starting from node {source}? \n"  

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
            Q = translate(Q, Q_state, args)

            truths.append(lines2[j + 1].rstrip("\n"))
            Q_list += [Q]
            i += 1
            j += 2
    
    graphSchema = GraphSchemaAnsOnly if args.prompt == "AnsOnly" else GraphSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, graphSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, graphSchema)
        else:
            raise Exception("Invalid format type.")

    res = []
    partial_res = []
    for i, answer in enumerate(answers):
        try:
            js_answer = json.loads(answers[i])
            answer = js_answer["final_answer"]
        except Exception as e:
            print(f"Error encountered at index {i}: {e}")
            res.append(0)
            partial_res.append(0)
            continue 
        if str(answer) == str(truths[i]):
            res.append(1)
        else:
            res.append(0)
        partial_res.append(1 - levenshtein(str(answer), str(truths[i])))

    log(Q_list, res, partial_res, answers, args)


if __name__ == "__main__":
    main()

