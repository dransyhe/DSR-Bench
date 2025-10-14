from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str


class GraphSchema(BaseModel):
    # Output schema for bsf and dfs
    steps: list[Step]
    final_answer: list[int]
    
class GraphSchemaAnsOnly(BaseModel):
    # Output schema for bsf and dfs
    final_answer: list[int]