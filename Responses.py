from pydantic import BaseModel
from typing import List
from DataTypes import President, Quiz

class GetQuizResponse(BaseModel):
    quiz: Quiz


class SubmitGuessResponse(BaseModel):
    correct: bool
    correct_answer: President


class GetStatsResponse(BaseModel):
    correct: int
    incorrect: int
    total: int
    histogram: List[int]