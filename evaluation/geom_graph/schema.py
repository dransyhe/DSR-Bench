from pydantic import BaseModel

class Step(BaseModel):
    explanation: str
    output: str

class GeomSchema(BaseModel):
    steps: list[Step]
    final_answer: list[list[float]]

class GeomSchemaAnsOnly(BaseModel):
    final_answer: list[list[float]]


# --- GED schemas: explicit graph representation ---

class GeomGraphOutput(BaseModel):
    nodes: list[list[float]]
    edges: list[list[list[float]]]

class GeomGEDSchema(BaseModel):
    steps: list[Step]
    final_answer: GeomGraphOutput

class GeomGEDSchemaAnsOnly(BaseModel):
    final_answer: GeomGraphOutput