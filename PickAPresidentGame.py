import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import Tables
from DataTypes import Quiz, President, Stats
from PlayerCache import PlayerCache
import random
from typing import Tuple

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


    def stats(
        self, 
        player: int, 
        last_n: int = 10
    ) -> Tuple[Stats, Stats]:
        """
        Return a Tuple of Stats objects for last_n and all time for the player.
        """
        
        sess = self.session_maker()
        
        # get the last_n records, right or wrong.
        last_n_total = sess.query(Tables.QuizRecord).filter(Tables.QuizRecord.player_id == player).order_by(Tables.QuizRecord.time.desc()).limit(last_n)
        last_n_correct = sum([ 1 for qr in last_n_total if qr.correct ])
        last_n_total = last_n_total.count()

        # get all records, right or wrong.
        all_time_total = sess.query(Tables.QuizRecord).filter(Tables.QuizRecord.player_id == player)
        all_time_correct = sum([ 1 for qr in all_time_total if qr.correct ])
        all_time_total = all_time_total.count()

        sess.close()

        last_n_stats = Stats(correct=last_n_correct, incorrect=last_n_total - last_n_correct)
        all_time_stats = Stats(correct=all_time_correct, incorrect=all_time_total - all_time_correct)

        return last_n_stats, all_time_stats


    def update_histogram(self):
        """
        For each player, get their score and update the histogram.
        """

        sess = self.session_maker()
        all_players = set([ qr.player_id for qr in sess.query(Tables.QuizRecord).all() ])
        sess.close()

        new_histogram = [0] * 11

        for player in all_players:
            lastn, alltime = self.stats(player)
            bucket = int(lastn.correct / (lastn.correct + lastn.incorrect) * 10)
            new_histogram[bucket] += 1


        total_value = sum(new_histogram)
        for i in range(len(new_histogram)):
            new_histogram[i] = new_histogram[i] / total_value

        self.histogram = new_histogram


