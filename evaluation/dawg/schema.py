from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str


class DAWGSchema(BaseModel):
    steps: list[Step]
    final_answer: list[list[str]]
    
class DAWGSchemaAnsOnly(BaseModel):
    final_answer: list[list[str]]
 