import openai
import os
import argparse
import json

from evaluation.eval import translate, predict, log
from evaluation.batch_eval import get_batch_results
from evaluation.utils import parse_arguments, str_to_int_list, levenshtein

from evaluation.priority_queue.schema import PriorityQueueSchema, PriorityQueueSchemaAnsOnly 


def main():

    args = parse_arguments()
    args.type = "priority_queue"
    args.operation = "compound"

    truths = []

    i = 0
    Q_list = []
    with open(f"generation/priority_queue/compound/compound_{args.mode}.txt", "r") as f:
        lines = f.readlines()
        while i < len(lines):
            i += 1

            if args.description == "full":
                Q_state = (
                    "A max priority queue stores items each as a (value, priority) pair, where items are served in order of highest priority.\n" + \
                    "It is implemented as a Fibonacci heap (a collection of heap-ordered trees linked in circular, doubly-linked lists, with lazy consolidation).\n" + \
                    "It has four kinds of operations:\n" + \
                    "1. insert(value, priority):\n" + \
                    "   a. Create a new singleton node with the given value and priority and add it to the root list.\n" + \
                    "   b. Update the pointer to the maximum root if needed.\n" + \
                    "2. delete: remove and return the element with the highest priority (extract_max):\n" + \
                    "   a. Remove the max root from the root list.\n" + \
                    "   b. Add each of its children to the root list, clearing their parent pointers.\n" + \
                    "   c. Consolidate the root list by linking roots of equal degree until all roots have distinct degrees.\n" + \
                    "   d. Update the pointer to the new maximum root.\n" + \
                    "3. raise_key(value, new_priority):\n" + \
                    "   a. Locate the node and increase its priority to new_priority (≥ current priority).\n" + \
                    "   b. If it now violates the heap property with its parent, cut it and add it to the root list, performing cascading cuts on marked parents.\n" + \
                    "   c. Update the pointer to the maximum root if needed.\n" + \
                    "4. decrease_key(value, new_priority):\n" + \
                    "   a. Locate the node and decrease its priority to new_priority (≤ current priority).\n" + \
                    "   b. If any child’s priority now exceeds the node’s, cut those children and add them to the root list, clearing their parent pointers.\n" + \
                    "After all operations, output the list of remaining (value, priority) pairs sorted by descending priority, breaking ties by insertion time (earlier inserts first).\n" + \
                    ""
                )
            else:
                Q_state = ("A priority queue stores items each as a (value, priority) pair. \n"
                    "It is implemented as a Fibonacci heap, with four kinds of operations:\n"
                    "1. insert(value,priority): add an element with the given value and priority.\n"
                    "2. delete: remove and return the element with the highest priority.\n"
                    "If multiple elements share that priority, remove the one inserted earliest.\n"
                    "3. raise_key(value,new_priority): increase the priority of the existing element valueto new_priority;\n"
                    "new_priority must be >= its current priority.\n"
                    "4. decrease_key(value,new_priority): decrease the priority of the existing element value to new_priority;\n"
                    "new_priority must be <= its current priority.\n"
                    "After all operations, output the list of remaining (value, priority) pairs sorted by descending priority,\n"
                    "breaking ties by insertion time (earlier inserts first).\n"
                )

            Q = (
                "You are given an empty priority queue initially.\n"
                "The final state is the list of (value, priority) pairs as produced by a level-order traversal of the Fibonacci-heap forest,\n"
                "where you visit all roots first, then all their children, then all grandchildren, and so on;\n"
                "within each level, nodes are listed in descending priority order (breaking ties by larger value first).\n"
                "Q: What is the state of the priority queue after the following operations:\n"
            )

            while i < len(lines) and "[" not in lines[i]:
                line = lines[i].strip()

                # INSERT
                if line.startswith("insert"):
                    # line == "insert (v,p)"
                    args_str = line[line.find("(")+1 : line.rfind(")")]   # "v,p"
                    v_str, p_str = args_str.split(",")
                    v, p = int(v_str.strip()), int(p_str.strip())
                    Q += f"(insert, {v}, {p})\n"

                # DELETE
                elif line == "delete":
                    Q += "(delete)\n"

                # RAISE_KEY
                elif line.startswith("raise_key"):
                    args_str = line[line.find("(")+1 : line.rfind(")")]
                    v_str, new_p_str = args_str.split(",")
                    v, new_p = int(v_str.strip()), int(new_p_str.strip())
                    Q += f"(raise_key, {v}, {new_p})\n"

                # DECREASE_KEY
                elif line.startswith("decrease_key"):
                    args_str = line[line.find("(")+1 : line.rfind(")")]
                    v_str, new_p_str = args_str.split(",")
                    v, new_p = int(v_str.strip()), int(new_p_str.strip())
                    Q += f"(decrease_key, {v}, {new_p})\n"

                i += 1
                
            if "deepseek-chat" in args.model:
                if args.prompt == "AnsOnly":
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                            '{ \n' +\
                            '    "final_answer": [[56, 23], [67, 25], [78, 62]] \n' +\
                            '}\n '
                else:
                    Q_state += "EXAMPLE JSON OUTPUT: \n" +\
                                '{ \n' +\
                                '    "steps": [{intermediate step 1}, {intermediate step 2}, ...], \n' +\
                                '    "final_answer": [[56, 23], [67, 25], [78, 62]] \n' +\
                                '}\n '

            Q = translate(Q, Q_state, args)

            truths.append(lines[i].strip())
            Q_list += [Q]
            i += 1

    priorityQueueSchema = PriorityQueueSchemaAnsOnly if args.prompt == "AnsOnly" else PriorityQueueSchema
    if args.batch:
        answers = get_batch_results(Q_list, args, priorityQueueSchema)
    else: 
        if args.format == "schema":
            answers = predict(Q_list, args, priorityQueueSchema)
        else:
            raise Exception("Invalid format type.")

    res = []
    partial_res = []
    for i in range(len(answers)):
        try:
            js_answer = json.loads(answers[i])
            answer = js_answer["final_answer"]
        except Exception as e:
            print(f"Error encountered.")
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

