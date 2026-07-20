from pydantic import BaseModel

class QueryRequest(BaseModel):
    question:str
    datasource:str="sales"
    type: str
