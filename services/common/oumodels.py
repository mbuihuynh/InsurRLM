from pydantic import BaseModel


class OutputData(BaseModel):
    name: str
    output: str