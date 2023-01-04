from pydantic import BaseModel
from typing import List
from DataTypes import President, Quiz, Stats

class GetQuizResponse(BaseModel):
    quiz: Quiz


class SubmitGuessResponse(BaseModel):
    correct: bool
    correct_answer: President


class GetStatsResponse(BaseModel):
    last_ten: Stats
    all_time: Stats
    histogram: List[int]