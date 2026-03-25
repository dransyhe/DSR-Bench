from pydantic import BaseModel
from typing import Optional

class Step(BaseModel):
    explanation: str
    output: str

class KDTSchema(BaseModel):
    # Output schema for heapify and compound
    steps: list[Step]
    final_answer: list[list[int]]

class KDTSchemaAnsOnly(BaseModel):
    # Answer only schema for heapify and compound
    final_answer: list[list[int]]


# --- TED schemas: nested tree representation ---

class KDTNodeSchema(BaseModel):
    point: list[int]
    left: Optional['KDTNodeSchema'] = None
    right: Optional['KDTNodeSchema'] = None

KDTNodeSchema.model_rebuild()

class KDTTEDSchema(BaseModel):
    steps: list[Step]
    final_answer: KDTNodeSchema

class KDTTEDSchemaAnsOnly(BaseModel):
    final_answer: KDTNodeSchema