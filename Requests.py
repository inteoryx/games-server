import pydantic
from pydantic import BaseModel

class GetQuizRequest(BaseModel):
    player_id: int

class SubmitGuessRequest(BaseModel):
    player_id: int
    quiz_id: int
    answer: str

class GetStatsRequest(BaseModel):
    player_id: int