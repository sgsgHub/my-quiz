import unittest

from validate_questions import validate_questions


class TestValidateQuestions(unittest.TestCase):
    def test_valid_question(self):
        questions = [
            {
                "category": "Prepositions of time",
                "question": "____ midnight",
                "full_answer": "At midnight",
                "answers": ["At", "On", "in"],
                "correct_answer": 1,
            }
        ]

        self.assertTrue(validate_questions(questions))

    def test_empty_questions(self):
        with self.assertRaises(ValueError):
            validate_questions([])

    def test_wrong_number_of_answers(self):
        questions = [
            {
                "question": "Test question",
                "answers": ["A", "B"],
                "correct_answer": 1,
            }
        ]

        with self.assertRaises(ValueError):
            validate_questions(questions)

    def test_invalid_correct_answer(self):
        questions = [
            {
                "question": "Test question",
                "answers": ["A", "B", "C"],
                "correct_answer": 4,
            }
        ]

        with self.assertRaises(ValueError):
            validate_questions(questions)

    def test_missing_raises_value_error(self):
        question = {
            "question": "Test question",
            "answers": ["A", "B", "C"],
            "correct_answer": 1,
        }

        with self.assertRaises(ValueError):
            validate_questions([question])

    def test_empty_category_raises_value_error(self):
        question = {
            "category": "",
            "question": "Test question",
            "answers": ["A", "B", "C"],
            "correct_answer": 1,
        }

        with self.assertRaises(ValueError):
            validate_questions([question])

    def test_whitespace_category_raises_value_error(self):
        question = {
            "category": "   ",
            "question": "Test question?",
            "answers": ["A", "B", "C"],
            "correct_answer": 1,
        }

        with self.assertRaises(ValueError):
            validate_questions([question])


if __name__ == "__main__":
    unittest.main()
