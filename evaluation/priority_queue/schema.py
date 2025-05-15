from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str

class PriorityQueueSchema(BaseModel):
    # Output schema for heapify and compound
    steps: list[Step]
    final_answer: list[list[int]]
    
class PriorityQueueSchemaAnsOnly(BaseModel):
    # Answer only schema for heapify and compound
    final_answer: list[list[int]]