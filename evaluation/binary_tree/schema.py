from pydantic import BaseModel
# from typing import Any

class Step(BaseModel):
    explanation: str
    output: str
    
class Traverse(BaseModel):
    pre_order: list[int]
    post_order: list[int]
    
class FullTraverse(BaseModel):
    pre_order: list[int]
    in_order: list[int]
    post_order: list[int]
    depth: int

class InsertSchema(BaseModel):
    # Schema for insert and delete operations
    steps: list[Step]
    final_answer: Traverse

class InsertSchemaAnsOnly(BaseModel):
    final_answer: Traverse

class TraverseSchema(BaseModel):
    # Schema for traversal operations
    steps: list[Step]
    final_answer: list[int]
    
class TraverseSchemaAnsOnly(BaseModel):
    final_answer: list[int]

class DepthSchema(BaseModel):
    # Schema for depth operations
    steps: list[Step]
    final_answer: int
    
class DepthSchemaAnsOnly(BaseModel):
    final_answer: int
    
class CompoundSchema(BaseModel):
    # Schema for compound operations
    steps: list[Step]
    final_answer: list[int]
    
class CompoundSchemaAnsOnly(BaseModel):
    final_answer: list[int]
    
def get_description(args):
    if args.description == "full":
        description = ("a hierarchical data structure in which each node holds a key (and optionally associated data) \n"
                       "and has at most two children, conventionally called left and right. What makes it a “search” tree \n"
                       "is its ordering rule: every key in a node’s left subtree is strictly less than the node’s key, \n"
                       "and every key in its right subtree is strictly greater. This invariant recurses down the tree, so starting \n"
                       "from the root you can locate, insert, or delete a key by repeatedly comparing and following the appropriate \n"
                       "child link—just like playing a deterministic game of “higher or lower. \n"
                       "The depth of a binary search tree is the number of nodes on the longest path from the root to a leaf node. \n")
        if args.operation == "add":
            description += "To add a node to the binary search tree, start at the root and compare the value to be inserted with the value of the current node. \n" \
                "If the value is less than the current node's value, move to the left child; if it is greater, move to the right child. \n" \
                "Repeat this process until you find an empty spot in the tree where the new node can be inserted. \n"
        elif args.operation == "remove":
            description += "To remove a node from the binary search tree, first locate the node to be removed. \n" \
                "If the node has no children, simply remove it. If it has one child, remove the node and replace it with its child. \n" \
                "If it has two children, find the node's in-order predecessor (the largest value in its left subtree) or in-order successor (the smallest value in its right subtree), \n" \
                "replace the node's value with that of the predecessor/successor, and then remove the predecessor/successor from the tree. \n"
        elif args.operation == "inorder":
            description += "In-order traversal of a binary search tree visits the nodes in ascending order. \n" \
                "To perform an in-order traversal, recursively visit the left subtree, then the current node, and finally the right subtree. \n"
        elif args.operation == "preorder":  
            description += "Pre-order traversal of a binary search tree visits the nodes in the order: current node, left subtree, right subtree. \n" \
                "To perform a pre-order traversal, recursively visit the current node, then the left subtree, and finally the right subtree. \n"
        elif args.operation == "postorder":
            description += "Post-order traversal of a binary search tree visits the nodes in the order: left subtree, right subtree, current node. \n" \
                "To perform a post-order traversal, recursively visit the left subtree, then the right subtree, and finally the current node. \n"
    else:
        description = ("A binary search tree is a tree where each node has at most two children, "
                    "and the left child is less than or equal to the parent node, while the right child is greater than the parent node. \n"
                )
    if args.operation == "depth":
        description += "Depth of a binary search tree is the distance from the root node to the deepest leaf node. \n"
    return description