import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, levenshtein

from evaluation.dsu.schema import DSUSchema, DSUSchemaAnsOnly


def main():
    args = parse_arguments()
    args.type = "dsu"
    args.operation = "compound"

    truths = []
    Q_list = []

    # Path to the generated DSU instances
    filepath = f"generation/dsu/compound/compound_{args.mode}.txt"
    with open(filepath, "r") as f:
        # strip lines and skip empty ones
        lines = [line.strip() for line in f if line.strip()]

    i = 0
    # Iterate through each instance in the file
    while i < len(lines):
        raw_items = json.loads(lines[i])

        if args.description == "full":
            description = (
                "A Disjoint-Set Union (DSU) maintains a partition of elements into disjoint sets. Each set is a tree, leading to a forest of trees.\n" 
                "It supports two operations:\n"
                " - find(x): Return the root of the set containing x by following parent pointers (with path compression).\n"
                " - union(x, y): Merge the set containing x and the set containg y.\n"
                "The union function is done by finding the roots of the set containing x and the set containing y.\n"
                "If the roots are different, we merge the two sets by attaching the root with higher rank as the parent of the root with lower rank.\n"
                "If the ranks are equal, we can pick the root of the set containing x as the parent and increment its rank by 1.\n"
                "Here, rank is a heuristic upper bound on the height of v's tree, which increases when two equal-rank trees merge.\n"
                "Initially, each element x in the input list is a set. It is its own parent, and its rank is 0.\n"
            )
        else:
            description = (
                "You want to create a Disjoint Set Union (DSU).\n"
                "It supports two operations:\n"
                " - find(x): Returns the representative (root) element of the set containing element x. \n"
                " - union(x, y): Merges (i) the set containing element x and (ii) the set containing element y.\n"
                " During merging, always attach the lower-rank root under the higher-rank one (and if ranks are equal, pick the root of the set containing x and increment its rank).\n"
            )

        Q_state = (
            description
            + "When asked for the final state of the DSU, return a list of find(x) for each x in the initial list, in their original order.\n"
        )  

        if "deepseek-chat" in args.model:
            if args.prompt == "AnsOnly":
                Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                        '{ \n' +\
                        '    "final_answer": [88, 24, 32, 24, 88, 32, 48, 88]\n' +\
                        '}\n '
            else:
                Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                            '    "final_answer": [88, 24, 32, 24, 88, 32, 48, 88, 24, 88] \n' +\
                            '}\n '
                            
        Q = f"Q: The initial list of elements is: {raw_items}. What is the final state of the DSU after the following union operations?\n"

        i += 1
        while i < len(lines) and lines[i].startswith("union"):  # e.g., union(0, 3)
            Q += lines[i] + "\n"
            i += 1

        truth = lines[i]
        truths.append(truth)

        Q_list.append(translate(Q, Q_state, args))
        i += 1

    dsu_schema = DSUSchemaAnsOnly if args.prompt == "AnsOnly" else DSUSchema

    if args.batch:
        answers = get_batch_results(Q_list, args, dsu_schema)
    else:
        if args.format == "schema":
            answers = predict(Q_list, args, dsu_schema)
        else:
            raise Exception("Invalid format type. Use 'schema'.")

    res = []
    partial_res = []
    for i, (ans, truth) in enumerate(zip(answers, truths)):
        try:
            js = json.loads(ans)
            final_answer = js.get("final_answer")
        except Exception as e:
            print(f"Error encountered: {e}")
            res.append(0)
            partial_res.append(0)
            continue

        if str(final_answer) == str(truth):
            res.append(1)
        else:
            print(f"Failed case {i} - Answer: {final_answer}")
            print(f"Failed case {i} - Truth: {truth}")  
            res.append(0)
        partial_res.append(1 - levenshtein(str(final_answer), str(truth)))

    # Log results
    log(Q_list, res, partial_res, answers, args)


if __name__ == "__main__":
    main()
