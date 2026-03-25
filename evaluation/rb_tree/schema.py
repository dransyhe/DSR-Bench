from pydantic import BaseModel
from typing import Optional

class Step(BaseModel):
    explanation: str
    output: str

class RBTreeSchema(BaseModel):
    # Schema for insert and delete operations
    steps: list[Step]
    final_answer: list[list[int]]

class RBTreeSchemaAnsOnly(BaseModel):
    final_answer: list[list[int]]


# --- TED schemas: nested tree representation ---

class RBTreeNodeSchema(BaseModel):
    value: int
    color: str  # "r" or "b"
    left: Optional['RBTreeNodeSchema'] = None
    right: Optional['RBTreeNodeSchema'] = None

RBTreeNodeSchema.model_rebuild()

class RBTreeTEDSchema(BaseModel):
    steps: list[Step]
    final_answer: RBTreeNodeSchema

class RBTreeTEDSchemaAnsOnly(BaseModel):
    final_answer: RBTreeNodeSchema