from PickAPresidentGame import PickAPresidentGame
import unittest
import random

class TestPAPG(unittest.TestCase):

    """
    Test Cases

    1. get_quiz
        a. get a quiz
        b. get a quiz repeatedly
        c. get a quiz with different player ids

    2. submit_guess
        a. submit a correct guess
        b. submit an incorrect guess
        c. submit a guess with a different player id

    3. stats
        a. stats with no history
        b. stats with a history

    4. played_quizzes
        a. get played quizzes with no history
        b. get played quizzes with a history
        c. get played quizzes with a history with different player ids

    """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.papg = PickAPresidentGame("test_pap.db")

    def test_get_quiz(self):
        quiz = self.papg.get_quiz(1)
        self.assertIsNotNone(quiz)

    def test_repeated_get_quiz(self):
        for _ in range(3):
            quiz = self.papg.get_quiz(1)
            self.assertIsNotNone(quiz)

    def test_get_quiz_different_player_ids(self):
        for player_id in range(1, 4):
            quiz = self.papg.get_quiz(player_id)
            self.assertIsNotNone(quiz)

    def test_submit_answer(self):
        quiz = self.papg.get_quiz(1)
        returned_answers = set()
        for choice in quiz.choices:
            returned_answers.add(self.papg.guess(1, quiz.id, choice.president_id).president_id)

        # Confirm that only one answer was returned and that it was one of the choices
        self.assertEqual(len(returned_answers), 1)
        self.assertTrue(returned_answers.pop() in set(c.president_id for c in quiz.choices))

    def test_stats(self):
        random_id = random.randint(1, 100_000_000_000)
        lastn_stats, all_stats = self.papg.stats(random_id)

        self.assertEqual(lastn_stats.correct, 0)
        self.assertEqual(lastn_stats.incorrect, 0)
        self.assertEqual(all_stats.correct, 0)
        self.assertEqual(all_stats.incorrect, 0)

    def test_stats_with_history(self):
        random_id = random.randint(1, 100_000_000_000)

        correct = 0
        incorrect = 0
        for _ in range(100):
            quiz = self.papg.get_quiz(random_id)
            answer = random.choice(quiz.choices)
            guess = self.papg.guess(random_id, quiz.id, answer.name)
            if guess.president_id == answer.president_id:
                correct += 1
            else:
                incorrect += 1

        lastn_stats, all_stats = self.papg.stats(random_id)
        self.assertEqual(all_stats.correct, correct)
        self.assertEqual(all_stats.correct + all_stats.incorrect, correct + incorrect)




if __name__ == '__main__':
    unittest.main()