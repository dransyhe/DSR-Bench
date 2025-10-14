from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str


class TrieSchema(BaseModel):
    # Output schema for access and search 
    steps: list[Step]
    final_answer: list[str]
    
class TrieSchemaAnsOnly(BaseModel):
    # Answer only schema for access and search 
    final_answer: list[str]
