import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.eval import prompt_list, model_list
from evaluation.utils import list_to_str

from evaluation.r_tree.schema import RTSchema, RTSchemaAnsOnly


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default="gpt-4o-mini", help='name of LM (default: gpt-4o-mini)', choices=model_list)
    parser.add_argument('--mode', type=str, default="easy", help='mode (default: easy)')
    parser.add_argument('--prompt', type=str, default="none", help='prompting techniques (default: none)', choices=prompt_list)
    parser.add_argument('--T', type=float, default=0, help='temprature (default: 0)')
    parser.add_argument('--token', type=int, default=1500, help='max token (default: 400)')
    parser.add_argument('--batch', type=bool, default=False, help='batch eval if True (default: False)')
    parser.add_argument('--format', type=str, default="schema", help='type of structured format method, schema or function (default: schema)')
    args = parser.parse_args()
    args.type = "r_tree"
    args.operation = "search"

    i = 0
    Q_list = []

    post_truths = []
    
    alphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    with open(f"generation/kd_tree/search/rt_search_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        Q_state = "Suppose you have an empty R tree. You should construct a R tree with a set of given rectangles \n " + \
            "defined by four values (min of x, min of y, max of x, max of y). \n" +\
            "Each triangle is associated to some data in the form of a upper case alphabet. \n" +\
            "After the construction, find the ."
        
        while i < len(lines):
            
            if "Points" in lines[i]:
                Q = lines[i].split(":")[1]
                Q = f"Construct a KD-tree with the following points: {Q}\n"
                Q += "After that, please answer the following question:\n" + \
                    "What is the pre-order traversal of the tree? Output in a nested list like the input. \n"
                i += 1
                Q = translate(Q, Q_state, args)
                Q_list += [Q]
            elif "Traversal" in lines[i]:
                values = lines[i].split(":")[1].strip()
                post_truths.append(values)
                i += 1
            elif "Tree" in lines[i]:
                i += 1
                pass

    traverseSchema = RTSchema if args.prompt == "AnsOnly" else RTSchemaAnsOnly
    if args.batch:
        answers = get_batch_results(Q_list, args, traverseSchema)
        
        # answers = [] 
        # with open("log/kd_tree/construction/o3-mini-moon/batch_67fd86eda04c81908a9081ac282091ae_output.jsonl", "r") as f_jsonl:
        #     for line in f_jsonl:
        #         data = json.loads(line)
        #         answer = data["response"]["body"]["choices"][0]["message"]["content"]
        #         answers.append(answer)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, traverseSchema)
        else:
            raise Exception("Invalid format type.")
        
    post_answers = []
    for answer in answers:
        try:
            js_answer = json.loads(answer)
            post_answers.append(js_answer["final_answer"])
        except Exception as e:
            print(f"Error encountered probably due to short of tokens.")
            post_answers.append("")
            continue
        
    score = []

    for i in range(len(post_answers)):
        if list_to_str(post_answers[i]).strip() == list_to_str(post_truths[i]).strip():
            score.append(1)
        else:
            score.append(0)
            print(repr(list_to_str(post_answers[i]).strip()))
            print(repr(list_to_str(post_truths[i]).strip()))
            
            
 
    log(Q_list, score, answers, args)

if __name__ == "__main__":
    main()
