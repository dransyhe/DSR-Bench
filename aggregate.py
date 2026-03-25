import os
import glob
import re
import statistics
import csv 

# Define the variables
models = ["qwen3:8b"]  # "mixtral:8x7b", "phi4-reasoning:14b", "qwen3:8b"
modes = [ "hard"]  
prompts = ["AnsOnly"] # "none", "0-CoT", "CoT", "k-shot", 
Ts = [0.5]
tokens = [15000]

#=======================================================================
# Here you can set which set of aggregated stats you want to print
partial = False
if partial:
    print("Printing accuracy associated with edit distance error")
else:
    print("Printing accuracy associated with 0-1 error")
#=======================================================================

# Number of trials
num_trials = 3

# Dictionary for types and operations
ds_ops = {
    # "array": ["access", "delete", "insert", "reverse", "search"],
    # "skip_list": ["compound"],
    # "queue": ["compound"],
    # "stack": ["compound"],
    # "priority_queue": ["compound"],
    # "hashmap": ["compound"],
    # "trie": ["compound"],
    # "suffix_tree": ["construct"],
    # "binary_tree": ["insert", "remove", "inorder", "preorder", "postorder", "depth", "compound"],
    # "rb_tree": ["construct", "compound"],
    # "b_plus_tree": ["compound"],
    # "heap": ["compound", "heapify"], 
    # "graph": ["bfs", "dfs"],
    # "dsu": ["compound"],
    # "lru_cache": ["cache"],
    # "dawg": ["compound"],
    # "bloom_filter": ["compound"],
    # "kd_tree": ["construct_d5"],
    "kd_heap": ["compound_d5"],
    "geom_graph": ["construct_5d"],
    
    # "kd_heap":["compound_d1","compound_d2","compound_d3", "compound_d5"],
    # "kd_tree":["construct_d1","construct_d2","construct_d3", "construct_d5"],
    # "geom_graph": ["construct_1d", "construct_2d", "construct_3d", "construct_5d"],
    
    # "kd_tree": ["construct_moon", "construct_circle", "construct_blob"],
    
    # "kd_tree": ["construct_d5"],
    # "kd_heap":["compound_d5"],
    # "geom_graph": ["construct_2d"],
    
}

# Regex pattern to extract accuracy from the prompt.txt file
accuracy_pattern = re.compile(r"Accuracy\s*=\s*([\d\.]+)")
partial_accuracy_pattern = re.compile(r"Partial Accuracy\s*=\s*([\d\.]+)")

# Dictionary to store accuracies for each scenario
results = {}

# Iterate over all combinations of type, operation, model, mode, and prompt
for type_var, operations in ds_ops.items():
    for operation in operations:
        for model in models:
            for mode in modes:
                for prompt in prompts:
                    for T in Ts: 
                        for token in tokens: 
                            # Construct expected directory pattern
                            base_dir = f"log/{type_var}/{operation}"
                            search_pattern = f"{model}-*{mode}-*{T}-*{token}-*{prompt}*"
                            
                            # Find directories matching the pattern
                            matching_dirs = glob.glob(os.path.join(base_dir, f"{search_pattern}"))
                            # print(f"Matching directories: {matching_dirs}")

                            # Store accuracy values for this specific (model, type, operation, mode, prompt)
                            accuracy_values = []
                            partial_accuracy_values = []

                            for dir_path in matching_dirs:
                                if (prompt == "CoT" and "-0-CoT" not in dir_path) or \
                                   (prompt == "0-CoT" and "-0-CoT" in dir_path) or \
                                   (prompt != "0-CoT" and prompt != "CoT"):  
                                    prompt_file_path = os.path.join(dir_path, "prompt.txt")

                                    if os.path.exists(prompt_file_path):
                                        with open(prompt_file_path, "r", encoding="utf-8") as f:
                                            content = f.read()

                                        # Extract accuracy from the file content
                                        accuracy_match = accuracy_pattern.search(content)
                                        if accuracy_match:
                                            accuracy_values.append(float(accuracy_match.group(1)))
                                            
                                        partial_accuracy_match = partial_accuracy_pattern.search(content)
                                        if partial_accuracy_match:
                                            partial_accuracy_values.append(float(partial_accuracy_match.group(1)))

                            # Compute mean and standard deviation if we have at least one value
                            if accuracy_values and len(accuracy_values) == num_trials:
                            # if accuracy_values:
                                mean_acc = statistics.mean(accuracy_values)
                                std_acc = statistics.stdev(accuracy_values) if len(accuracy_values) > 1 else 0.0
                            else:
                                mean_acc, std_acc = None, None  # No valid accuracy found
                                
                            if partial_accuracy_values and len(partial_accuracy_values) == num_trials:
                                mean_partial_acc = statistics.mean(partial_accuracy_values)
                                std_partial_acc = statistics.stdev(partial_accuracy_values) if len(partial_accuracy_values) > 1 else 0.0
                            else:
                                mean_partial_acc, std_partial_acc = None, None

                            # Store results
                            results[(model, type_var, operation, mode, prompt, T, token)] = (mean_acc, std_acc, mean_partial_acc, std_partial_acc)
        
# Decide the order of columns (prompts) you want:
prompts_order = [ "AnsOnly"]  # "none", "0-CoT", "CoT", "k-shot",

# print(results)
# Print a header row
# For example, tab-separated.  You could also do comma-separated if you prefer CSV.
print("DataStructure\tOperation\t" + "\t".join(prompts_order))

for ds_type, operations in ds_ops.items():
    # We can print a row for each operation
    for operation in operations:
        # Start the row with the data structure name and the operation
        # row = [ds_type, operation]
        row = []
        par_row = []
        
        # For each prompt in the desired order, look up mean and std in results
        for prompt in prompts_order:
            # Here, we assume single model/mode/T/token. 
            # If you have multiple, you can loop or pick which ones you want. 
            # Example picks the first from your lists:
            model = models[0]
            mode = modes[0]
            temperature = Ts[0]
            max_token = tokens[0]
            
            # print(ds_type, operation)
            # print(results.get(
            #     (model, ds_type, operation, mode, prompt, temperature, max_token),
            #     (None, None)
            # ))
            
            mean_acc, std_acc, par_mean_acc, par_std_acc = results.get(
                (model, ds_type, operation, mode, prompt, temperature, max_token),
                (None, None)
            )
            # if mean_acc is not None and len(accuracy_values) == num_trials:     # Note this is to check if we have enough trials
            if mean_acc is not None:
                # Format however you like: "0.95" or "0.95 ± 0.02"
                cell_value = f"{mean_acc:.2f} ± {std_acc:.2f}"
                # If you want the std: cell_value = f"{mean_acc:.2f} ± {std_acc:.2f}"
            else:
                cell_value = "N/A"
                
            if par_mean_acc is not None:
                # Format however you like: "0.95" or "0.95 ± 0.02"
                par_cell_value = f" {par_mean_acc:.2f} ± {par_std_acc:.2f}"
                # If you want the std: cell_value = f"{mean_acc:.2f} ± {std_acc:.2f}"
            else:
                par_cell_value = "N/A"
            
            row.append(cell_value)
            par_row.append(par_cell_value)
        
        # Print the row (tab-separated)
        if partial:
            print(";".join(par_row))
        else:
            print(";".join(row))
