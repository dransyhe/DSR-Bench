import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein, str_to_nested_float_list

from evaluation.geom_graph.schema import GeomSchema, GeomSchemaAnsOnly

def main():

    args = parse_arguments()
    args.type = "geom_graph"
    
    k = args.dim
    args.operation = f"construct_{k}d"
    
    i = 0
    j = 0
    Q_list = []
    truths = []
    
    if args.description == "full":
        description = ("A random geometric graph consists of nodes and edges. Each edge connects two nodes. \n" 
                        "To create a random geometric graph from input points, we calculate the euclidean distance between each pair of points. \n"
                        "If the distance is less than a given threshold, we add an edge between those two points, \n" 
                        "and assign edge weight of that edge equal to the euclidean distance between the its nodes. \n"
                        "Breadth-first search traverses the graph from a source node, and explores all neighbors of a node before moving to the level. \n"
                    )
    else:
        description = ""
    
    with open(f"generation/geom_graph/construct_{k}d/construct_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            
            if "Graph" in line:
                pass
            elif "Nodes" in line: 
                nodes = line.split(":")[-1].rstrip("\n")
                Q_state = description + "You should create a random geometric graph given the following data points: \n" + \
                    nodes + "\n" 
                    
            elif "Threshold" in line:
                threshold = line.split(":")[-1].rstrip("\n")
                Q_state += "The threshold for creating an edge is " + threshold + ". \n" 
            elif "From" in line:
                source = line.split(":")[-1].rstrip("\n")
                Q_state += "After the graph is created, perform a breath-first-search starting from node " + source + ". \n"
                "If there are multiple neighbors to explore for a given node, prioritize the neighbor with the smallest edge weight. \n"
            elif "BFS" in line:
                bfs = line.split(":")[-1].rstrip("\n")
                truths.append(bfs)
                
                Q = f"Q: What is the final states of the graph? Output the breath-first-search of nodes represented by their original coordinate. \n"
                
                if "deepseek-chat" in args.model:
                    if args.prompt == "AnsOnly":
                        Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "final_answer": [[53.12, 73.37]. [47.26, 4.27], [3.12, 84.6], [15.27, 91.35]] \n' +\
                                '}\n '
                    else:
                        Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                    '{ \n' +\
                                    '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                    '    "final_answer": [[53.12, 73.37]. [47.26, 4.27], [3.12, 84.6], [15.27, 91.35]] \n' +\
                                    '}\n '
                    
                Q = translate(Q, Q_state, args) 
                Q_list += [Q]
            
            i += 1
    print(len(Q_list))
    # 1/0
    
    graphSchema = GeomSchemaAnsOnly if args.prompt == "AnsOnly" else GeomSchema
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
        
        print(repr(answer))
        print(repr(truths[i]))
        # answer = str_to_nested_float_list(answer)
        truths[i] = str_to_nested_float_list(truths[i])
        if str(answer) == str(truths[i]):
            res.append(1)
        else:
            res.append(0)
            print(f"Answer: {str(answer)}")
            print(f"Truth: {str(truths[i])}")
        partial_res.append(1 - levenshtein(str(answer), str(truths[i])))

    log(Q_list, res, partial_res, answers, args)


if __name__ == "__main__":
    main()

