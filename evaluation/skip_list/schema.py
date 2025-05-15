from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str


class SkipListSchema(BaseModel):
    # Output schema for access and search 
    steps: list[Step]
    final_answer: list[list[int]]
    
class SkipListSchemaAnsOnly(BaseModel):
    # Answer only schema for access and search 
    final_answer: list[list[int]]
