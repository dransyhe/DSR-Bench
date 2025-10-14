from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str

class QueueSchema(BaseModel):
    # Output schema for heapify and compound
    steps: list[Step]
    final_answer: list[str]
    
class QueueSchemaAnsOnly(BaseModel):
    # Answer only schema for heapify and compound
    final_answer: list[str]