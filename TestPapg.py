import unittest
from PickAPresidentGame import PickAPresidentGame
import random
from DataTypes import Stats
from collections import deque

class TestPapg(unittest.TestCase):
    
    def test_played_quizzes(self):
        game = PickAPresidentGame("test_pap.db")
        self.assertEqual(game.played_quizzes(1134), set())

    def test_get_quiz(self):
        game = PickAPresidentGame("test_pap.db")
        self.assertIsNotNone(game.get_quiz(1))


    def test_guess(self):
        game = PickAPresidentGame("test_pap.db")
        quiz = game.get_quiz(2)
        self.assertIsNotNone(quiz)

        # pick a number between 10 and 100 billion
        player_id = random.randint(10, 100_000_000_000)
        
        self.assertEqual(game.played_quizzes(player_id), set())
        
        lastn, alltime = game.stats(player_id)
        
        self.assertEqual(lastn.correct, 0)
        self.assertEqual(lastn.incorrect, 0)
        self.assertEqual(alltime.correct, 0)
        self.assertEqual(alltime.incorrect, 0)

        correct, incorrect = 0, 0
        quizes = set()
        last_ten = deque(maxlen=10)
        guess_on = 100

        for _ in range(guess_on):
            quiz = game.get_quiz(player_id)
            self.assertIsNotNone(quiz)
            quizes.add(quiz.id)
            choice = random.choice(quiz.choices)
            result = game.guess(player_id, quiz.id, choice.president_id)
            if result.president_id == choice.president_id:
                correct += 1
                last_ten.append(True)
            else:
                incorrect += 1
                last_ten.append(False)

        lastn, alltime = game.stats(player_id)
        self.assertEqual(alltime.correct, correct)
        self.assertEqual(alltime.incorrect, incorrect)
        self.assertEqual(lastn.correct, sum(last_ten))
        self.assertEqual(lastn.incorrect, len(last_ten) - sum(last_ten))






if __name__ == '__main__':
    unittest.main()
