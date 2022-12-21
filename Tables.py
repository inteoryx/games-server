
"""
Define the tables that are used by the games-server service.

president - id, name, imageSrc

quiz -
    id,
    quote,
    correctAnswer - president id,


quizRecord - A player has played a quiz.
    id,
    quizId - id of the quiz that was played,
    playerId - id of the player,
    guess - id of the president that was guessed,
    correct - boolean,
    time - time that the quiz was played,

"""

import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class President(Base):
    __tablename__ = "president"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    image = Column(String)
    
    def __repr__(self):
        return f"President(id={self.id}, name={self.name}, image={self.image})"


class Quiz(Base):
    __tablename__ = "quiz"
    id = Column(Integer, primary_key=True, autoincrement=True)
    quote = Column(String)
    correct_answer = Column(String)
    choices = Column(String)

    def __repr__(self):
        return f"Quiz(id={self.id}, quote={self.quote}, correct_answer={self.correct_answer}, choices={self.choices})"


class QuizRecord(Base):
    __tablename__ = "quizRecord"
    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id"))
    player_id = Column(Integer)
    guess = Column(Integer)
    correct = Column(Boolean)
    time = Column(DateTime, default=sqlalchemy.func.now())

    player_id_index = Index(
        "player_id_index", 
        "player_id"
    )

    def __repr__(self):
        return f"QuizRecord(id={self.id}, quiz_id={self.quiz_id}, player_id={self.player_id}, guess={self.guess}, correct={self.correct}, time={self.time})"
