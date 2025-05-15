from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str

class GraphSchema(BaseModel):
    steps: list[Step]
    final_answer: list[str]
    
class GraphSchemaAnsOnly(BaseModel):
    final_answer: list[str]