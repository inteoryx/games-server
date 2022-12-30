"""
games-server uses fastapi to provide the games service.
"""
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse
from threading import Lock
import uvicorn
from PickAPresidentGame import PickAPresidentGame
import os
from fastapi.staticfiles import StaticFiles

import Requests
import Responses

app = fastapi.FastAPI()
papg = PickAPresidentGame("pap.db")

origins = [
    "http://localhost:5000",
    "localhost:5000",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/getQuiz")
def get_quiz(r: Requests.GetQuizRequest) -> Responses.GetQuizResponse:
    quiz = papg.get_quiz(r.player_id)
    resp = Responses.GetQuizResponse(
        quiz=quiz
    )
    return resp


@app.post("/submitGuess")
def submit_guess(r: Requests.SubmitGuessRequest) -> Responses.SubmitGuessResponse:
    correct = papg.guess(r.player_id, r.quiz_id, r.answer)
    resp = Responses.SubmitGuessResponse(
        correct=correct.name == r.answer,
        correct_answer=correct

    )
    return resp


@app.post("/getStats")
def get_stats(r: Requests.GetStatsRequest) -> Responses.GetStatsResponse:
    correct, total = papg.stats(r.player_id)
    resp = Responses.GetStatsResponse(
        correct=correct,
        total=total,
        incorrect=total - correct,
        histogram=[elem * 100 for elem in papg.histogram]
    )
    return resp


if __name__ == "__main__":
    print("Starting server...")
    try:
        papg.update_histogram()
    except ZeroDivisionError:
        pass
    # allow cross origin requests
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    