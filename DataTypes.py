import pydantic
from typing import List

class President(pydantic.BaseModel):
    president_id: int
    name: str
    image: str


class Quiz(pydantic.BaseModel):
    id: int
    quote: str
    choices: List[President]


class Stats(pydantic.BaseModel):
    correct: int
    incorrect: int