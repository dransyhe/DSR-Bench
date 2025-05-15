from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str

class HeapSchema(BaseModel):
    # Output schema for heapify and compound
    steps: list[Step]
    final_answer: list[int]
    
class HeapSchemaAnsOnly(BaseModel):
    # Answer only schema for heapify and compound
    final_answer: list[int]