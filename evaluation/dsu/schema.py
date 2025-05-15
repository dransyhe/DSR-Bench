from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str

class DSUSchema(BaseModel):
    steps: list[Step]
    final_answer: list[int]
    
class DSUSchemaAnsOnly(BaseModel):
    final_answer: list[int]