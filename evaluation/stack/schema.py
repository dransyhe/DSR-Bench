from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str

class StackSchema(BaseModel):
    # Output schema for heapify and compound
    steps: list[Step]
    final_answer: list[int]
    
class StackSchemaAnsOnly(BaseModel):
    # Answer only schema for heapify and compound
    final_answer: list[int]