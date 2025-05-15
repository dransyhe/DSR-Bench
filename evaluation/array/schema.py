from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str


class AccessSchema(BaseModel):
    # Output schema for access and search 
    steps: list[Step]
    final_answer: int
    
class AccessSchemaAnsOnly(BaseModel):
    # Answer only schema for access and search 
    final_answer: int
    
class DeleteSchema(BaseModel):
    # Output schema for delete, insert, reverse
    steps: list[Step]
    final_answer: list[int]
    
class DeleteSchemaAnsOnly(BaseModel):
    # Answer only schema for delete, insert, reverse
    final_answer: list[int]


def get_description(args):
    # Get the description based on the mode
    if args.description == "full":
        description = "An array is a list of elements, each indexed by a number starting from 0. The elements can be accessed using their index. \n"
    else:
        description = "" 
    return description
    