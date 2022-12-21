import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import Tables
from DataTypes import Quiz, President
from PlayerCache import PlayerCache
import random

class PickAPresidentGame:

    """
    This class provides the logic for the Pick A President Game.
    
    Load all quiz objects from the database.

    Provide a quiz when asked.

    Check whether a submission is correct or not.

    Store guess records.

    Provide a histogram of accuracy.
    """

    def __init__(self, db) -> None:
        # open sqlite database with Write Ahead Logging
        engine = create_engine(f"sqlite:///{db}?mode=wal")
        #engine = create_engine(f"sqlite:///{db}")
        self.session_maker = sessionmaker(bind=engine)

        sess = self.session_maker()
        all_quizzes = [ q for q in sess.query(Tables.Quiz).all() ]
        self.all_presidents = {
            p.name: President(president_id=p.id, name=p.name, image=p.image)
            for p in sess.query(Tables.President).all()
        }
        sess.close()
        
        self.pc = PlayerCache(1_000)
        self.quizzes = set(all_quizzes)
        self.quiz_map = { q.id: q for q in all_quizzes }
        self.histogram = [0] * 11

    def played_quizzes(self, player):
        """
        Return a set of the quizzes played by the player.
        """

        cached = self.pc.get(player)
        if cached:
            return cached

        sess = self.session_maker()
        played = set([ q for q in sess.query(Tables.QuizRecord).filter(Tables.QuizRecord.player_id == player).all() ])
        sess.close()

        self.pc.put(player, played)
        return played


    def get_quiz(self, player):
        """
        Return a new quiz for the player.
        """

        played = self.played_quizzes(player)
        unplayed = self.quizzes - played
        if len(unplayed) == 0:
            return None

        quiz = random.choice(list(unplayed))
        choices = quiz.choices.split(",")
        result = Quiz(
            id = quiz.id,
            quote = quiz.quote,
            choices = [ self.all_presidents[p] for p in choices ],
            correct_answer = self.all_presidents[quiz.correct_answer]
        )

        return result

    def guess(self, player, quiz_id, answer):
        """
        A player has made a guess.  Record the guess and return the correct answer.
        """

        quiz = self.quiz_map[quiz_id]
        correct = answer == quiz.correct_answer
        print(answer, quiz.correct_answer, correct)

        sess = self.session_maker()
        qr = Tables.QuizRecord(
            player_id = player,
            quiz_id = quiz_id,
            guess = answer,
            correct = correct
        )
        sess.add(qr)
        sess.commit()
        sess.close()

        # Update the cache
        played = self.played_quizzes(player)
        played.add(quiz_id)

        return self.all_presidents[quiz.correct_answer]


    def stats(self, player, last_n=10):
        """
        Return a tuple (correct, total) for the last n quizzes.
        """
        
        sess = self.session_maker()
        quiz_history = sess.query(Tables.QuizRecord).filter(Tables.QuizRecord.player_id == player).order_by(Tables.QuizRecord.time.desc()).limit(last_n).all()
        
        sess.close()

        return (sum([ 1 for q in quiz_history if q.correct ]), len(quiz_history))

    def update_histogram(self):
        """
        For each player, get their score and update the histogram.
        """

        sess = self.session_maker()
        all_players = set([ qr.player_id for qr in sess.query(Tables.QuizRecord).all() ])
        sess.close()

        new_histogram = [0] * 11

        for player in all_players:
            correct, total = self.stats(player)
            bucket = int(correct / total * 10)
            new_histogram[bucket] += 1


        total_value = sum(new_histogram)
        for i in range(len(new_histogram)):
            new_histogram[i] = new_histogram[i] / total_value

        self.histogram = new_histogram


