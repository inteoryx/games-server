import unittest
from PickAPresidentGame import PickAPresidentGame
import random

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
        self.assertTrue(game.guess(player_id, quiz.id, quiz.correct_answer))
        self.assertEqual(game.played_quizzes(player_id), {quiz.id})

        self.assertEqual(game.stats(player_id), (1, 1))

        # make an incorrect guess
        self.assertFalse(game.guess(player_id, quiz.id, quiz.correct_answer + " something else"))
        self.assertEqual(game.stats(player_id), (1, 2))


if __name__ == '__main__':
    unittest.main()
