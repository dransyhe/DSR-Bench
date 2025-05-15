from pydantic import BaseModel
# from typing import Any

class Step(BaseModel):
    explanation: str
    output: str
    
class Tuple(BaseModel):
    key: int
    value: int
    
class Bucket(BaseModel):
    number: int
    contents: list[Tuple]

class HashMapSchema(BaseModel):
    # Output schema for hashmap compound
    steps: list[Step]
    final_answer: list[Bucket]
    
class HashMapSchemaAnsOnly(BaseModel):
    # Output schema for hashmap compound
    final_answer: list[Bucket]