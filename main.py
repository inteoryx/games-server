"""
games-server uses fastapi to provide the games service.
"""
import fastapi
from fastapi import File

import uvicorn
# allow cors
from fastapi.middleware.cors import CORSMiddleware

from PickAPresidentGame import PickAPresidentGame

import Requests
import Responses

import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("port", type=int, help="port number to run server on")
argparser.add_argument("db", type=str, help="path to database file")
argparser.add_argument("--test", help="Start in test mode (using in memory copy of db).")
args = argparser.parse_args()

app = fastapi.FastAPI()
papg = PickAPresidentGame(args.db)

origins = [
    "http://localhost:3000/",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    max_age=3600,
)


@app.post("/s/getQuiz")
def get_quiz(r: Requests.GetQuizRequest) -> Responses.GetQuizResponse:
    print("Getting quiz.")
    quiz = papg.get_quiz(r.player_id)
    print(quiz)
    resp = Responses.GetQuizResponse(
        quiz=quiz
    )
    print(resp)
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
    lastn, alltime = papg.stats(r.player_id)
    resp = Responses.GetStatsResponse(
        last_ten=lastn,
        all_time=alltime,
        histogram=[elem * 100 for elem in papg.histogram]
    )
    return resp


if __name__ == "__main__":
    print("Starting server...")
    try:
        papg.update_histogram()
    except ZeroDivisionError:
        pass

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=args.port,
        log_level="info",
    )
    
    