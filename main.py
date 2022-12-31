"""
games-server uses fastapi to provide the games service.
"""
import fastapi
from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse
from threading import Lock
import uvicorn
from PickAPresidentGame import PickAPresidentGame
import os
from fastapi.staticfiles import StaticFiles
import sys

import Requests
import Responses

app = fastapi.FastAPI()
papg = PickAPresidentGame("pap.db")



@app.post("/s/getQuiz")
def get_quiz(r: Requests.GetQuizRequest) -> Responses.GetQuizResponse:
    quiz = papg.get_quiz(r.player_id)
    resp = Responses.GetQuizResponse(
        quiz=quiz
    )
    return resp


@app.post("/s/submitGuess")
def submit_guess(r: Requests.SubmitGuessRequest) -> Responses.SubmitGuessResponse:
    correct = papg.guess(r.player_id, r.quiz_id, r.answer)
    resp = Responses.SubmitGuessResponse(
        correct=correct.name == r.answer,
        correct_answer=correct

    )
    return resp


@app.post("/s/getStats")
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
    port_num = int(sys.argv[1])
    print("Starting server...")
    try:
        papg.update_histogram()
    except ZeroDivisionError:
        pass
    # allow cross origin requests
    uvicorn.run(app, host="0.0.0.0", port=port_num)
    
    