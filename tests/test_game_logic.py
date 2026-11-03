import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from game_logic import (
    calculate_percentage,
    calculate_score,
    check_answer,
    get_categories,
    get_questions_by_category,
)
from main import (
    ask_question,
    choose_category,
    get_valid_answer,
)


class TestGameLogic(unittest.TestCase):
    def test_get_categories_returns_unique_categories(self):
        questions = [
            {"category": "Prepositions of time"},
            {"category": "Prepositions of time"},
            {"category": "Prepositions of time"},
        ]

        self.assertEqual(get_categories(questions), ["Prepositions of time"])

    def test_get_categories_returns_empty_list(self):
        self.assertEqual(get_categories([]), [])

    def test_correct_answer(self):
        self.assertTrue(check_answer(2, 2))

    def test_wrong_answer(self):
        self.assertFalse(check_answer(1, 2))

    def test_ask_question_returns_true_for_correct_answer(self):
        item = {
            "question": "____ midday",
            "full_answer": "At midday",
            "answers": ["On", "At", "In"],
            "correct_answer": 2,
        }

        with patch("builtins.input", return_value="2"), redirect_stdout(StringIO()):
            result = ask_question(item, 1)

        self.assertTrue(result)

    def test_ask_question_returns_false_for_wrong_answer(self):
        item = {
            "question": "____ midday",
            "full_answer": "At midday",
            "answers": ["On", "At", "In"],
            "correct_answer": 2,
        }

        with patch("builtins.input", return_value="1"), redirect_stdout(StringIO()):
            result = ask_question(item, 1)

        self.assertFalse(result)

    def test_calculate_score_all_correct(self):
        self.assertEqual(calculate_score([True, True, True]), 3)

    def test_calculate_score_some_correct(self):
        self.assertEqual(calculate_score([True, False, True]), 2)

    def test_calculate_score_none_correct(self):
        self.assertEqual(calculate_score([False, False, False]), 0)

    def test_invalid_input_is_rejected_and_retried(self):
        with (
            patch("builtins.input", side_effect=["abc", "4", "2"]),
            redirect_stdout(StringIO()),
        ):
            result = get_valid_answer()

        self.assertEqual(result, 2)

    def test_calculate_percentage(self):
        self.assertEqual(calculate_percentage(2, 3), 67)

    def test_calculate_percentage_all_correct(self):
        self.assertEqual(calculate_percentage(3, 3), 100)

    def test_calculate_percentage_no_questions(self):
        self.assertEqual(calculate_percentage(0, 0), 0)

    def test_filter_questions_by_category(self):
        questions = [
            {"category": "One", "question": "Question 1"},
            {"category": "Two", "question": "Question 2"},
            {"category": "One", "question": "Question 3"},
        ]
        result = get_questions_by_category(questions, "One")

        self.assertEqual(len(result), 2)
        self.assertTrue(all(q["category"] == "One" for q in result))

    def test_filter_questions_returns_one_question(self):
        questions = [
            {"category": "Two", "question": "Question 1"},
        ]
        result = get_questions_by_category(questions, "Two")
        self.assertEqual(len(result), 1)

    def test_filter_questions_returns_empty_list(self):
        questions = [
            {"category": "One", "question": "Question 1"},
        ]
        result = get_questions_by_category(questions, "Two")
        self.assertEqual(result, [])

    def test_choose_category(self):
        questions = [{"category": "One"}, {"category": "Two"}]
        with patch("builtins.input", return_value="3"):
            result = choose_category(questions)

        self.assertEqual(result, "Two")

    def test_choose_category_retries_invalid_input(self):
        questions = [{"category": "One"}, {"category": "Two"}]
        with patch("builtins.input", side_effect=["abc", "4", "2"]):
            result = choose_category(questions)

        self.assertEqual(result, "One")


if __name__ == "__main__":
    unittest.main()
