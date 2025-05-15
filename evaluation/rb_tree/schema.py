from pydantic import BaseModel
from typing import List, Tuple
# from typing import Any

class Step(BaseModel):
    explanation: str
    output: str
    
class RBTreeSchema(BaseModel):
    # Schema for insert and delete operations
    steps: list[Step]
    final_answer: list[list[int]]

class RBTreeSchemaAnsOnly(BaseModel):
    final_answer: list[list[int]]