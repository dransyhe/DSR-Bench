from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str
    
class RTSchema(BaseModel):
    # Output schema for heapify and compound
    steps: list[Step]
    final_answer: list[str]
    
class RTSchemaAnsOnly(BaseModel):
    # Answer only schema for heapify and compound
    final_answer: list[str]
    
class ConstructionSchema(BaseModel):
    # Output schema for heapify and compound
    steps: list[Step]
    final_answer: list[list[float]]
    
class ConstructionSchemaAnsOnly(BaseModel):
    # Answer only schema for heapify and compound
    final_answer: list[list[float]]