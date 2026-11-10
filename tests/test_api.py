import os
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from api import app
from database import get_categories_from_db, get_questions_from_db

client = TestClient(app)


class TestQuizAPI(unittest.TestCase):
    def create_session(self):
        response = client.post("/quiz/session", json={})
        self.assertEqual(response.status_code, 200)
        return response.json()["session_id"]

    def test_root(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Quiz API is running"})

    def test_categories(self):
        response = client.get("/categories")
        self.assertEqual(response.status_code, 200)

        data = response.json()["categories"]
        self.assertIn("Prepositions of time", data)
        self.assertIn("Prepositions of movement", data)

    def test_questions_do_not_expose_correct_answer(self):
        response = client.get("/questions")
        self.assertEqual(response.status_code, 200)

        for question in response.json()["questions"]:
            self.assertNotIn("correct_answer", question)
            self.assertNotIn("full_answer", question)
            self.assertEqual(len(question["answers"]), 3)

    def test_correct_answer(self):
        session_id = self.create_session()

        response = client.post(
            "/quiz/answer",
            json={"session_id": session_id, "question_id": 1, "answer": 1},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["correct"])

    def test_wrong_answer(self):
        session_id = self.create_session()
        response = client.post(
            "/quiz/answer",
            json={"session_id": session_id, "question_id": 1, "answer": 2},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["correct"])

    def test_unknown_category_returns_404(self):
        response = client.get("/questions", params={"category": "Unknown category"})
        self.assertEqual(response.status_code, 404)

    def test_unknown_question_returns_404(self):
        session_id = self.create_session()
        response = client.post(
            "/quiz/answer",
            json={"session_id": session_id, "question_id": 9999, "answer": 1},
        )
        self.assertEqual(response.status_code, 404)

    def test_invalid_answer_returns_422(self):
        session_id = self.create_session()
        response = client.post(
            "/quiz/answer",
            json={"session_id": session_id, "question_id": 1, "answer": 4},
        )
        self.assertEqual(response.status_code, 422)

    def test_duplicate_answer_returns_409(self):
        session_id = self.create_session()
        payload = {
            "session_id": session_id,
            "question_id": 1,
            "answer": 1,
        }
        first_response = client.post("/quiz/answer", json=payload)
        self.assertEqual(first_response.status_code, 200)
        second_response = client.post("/quiz/answer", json=payload)
        self.assertEqual(second_response.status_code, 409)

    def test_answer_question_from_another_category(self):
        categories = get_categories_from_db()
        category_a = categories[0]
        category_b = categories[1]

        question_from_b = get_questions_from_db(category_b)[0]

        session_response = client.post(
            "/quiz/session",
            json={"category": category_a},
        )
        session_id = session_response.json()["session_id"]

        response = client.post(
            "/quiz/answer",
            json={
                "session_id": session_id,
                "question_id": question_from_b["id"],
                "answer": 1,
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Question does not belong to this session's category"
        )

    def test_complete_quiz_session(self):
        session_id = self.create_session()
        questions = get_questions_from_db()
        for question in questions:
            response = client.post(
                "/quiz/answer",
                json={
                    "session_id": session_id,
                    "question_id": question["id"],
                    "answer": question["correct_answer"],
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()["correct"])
        response = client.get(f"/quiz/session/{session_id}/score")
        self.assertEqual(response.status_code, 200)

        score = response.json()
        self.assertEqual(score["score"], len(questions))
        self.assertEqual(score["status"], "completed")
        response = client.post(
            "/quiz/answer",
            json={
                "session_id": session_id,
                "question_id": questions[0]["id"],
                "answer": questions[0]["correct_answer"],
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["detail"],
            "This quiz session is already completed",
        )


class TestAdminCategoryAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env_patcher = patch.dict(
            os.environ,
            {
                "ADMIN_USERNAME": "test-admin",
                "ADMIN_PASSWORD": "test-password",
            },
        )
        cls.env_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.env_patcher.stop()

    def auth(self):
        return ("test-admin", "test-password")

    def create_category(self):
        name = f"Test category {uuid4()}"

        response = client.post(
            "/admin/categories",
            json={"name": name},
            auth=self.auth(),
        )

        self.assertEqual(response.status_code, 201)
        return response.json()["category"]

    def test_rename_category(self):
        category = self.create_category()
        new_name = f"Renamed {uuid4()}"

        response = client.put(
            f"/admin/categories/{category['id']}",
            json={"name": new_name},
            auth=self.auth(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"]["name"], new_name)

        client.delete(
            f"/admin/categories/{category['id']}",
            auth=self.auth(),
        )

    def test_rename_to_existing_name_returns_409(self):
        category = self.create_category()

        response = client.put(
            f"/admin/categories/{category['id']}",
            json={"name": "Prepositions of time"},
            auth=self.auth(),
        )

        self.assertEqual(response.status_code, 409)

        client.delete(
            f"/admin/categories/{category['id']}",
            auth=self.auth(),
        )

    def test_delete_category_with_questions_returns_409(self):
        category = self.create_category()

        question_response = client.post(
            "/admin/questions",
            json={
                "category": category["name"],
                "question": "Temporary test question",
                "full_answer": "Test answer",
                "correct_answer": 1,
                "answers": ["One", "Two", "Three"],
            },
            auth=self.auth(),
        )

        self.assertEqual(question_response.status_code, 201)
        question_id = question_response.json()["question_id"]

        response = client.delete(
            f"/admin/categories/{category['id']}",
            auth=self.auth(),
        )

        self.assertEqual(response.status_code, 409)

        # Clean up the test question and category.
        client.delete(
            f"/admin/questions/{question_id}",
            auth=self.auth(),
        )
        client.delete(
            f"/admin/categories/{category['id']}",
            auth=self.auth(),
        )

    def test_delete_category_with_quiz_session_returns_409(self):
        category = self.create_category()

        session_response = client.post(
            "/quiz/session",
            json={"category": category["name"]},
        )

        self.assertEqual(session_response.status_code, 200)

        response = client.delete(
            f"/admin/categories/{category['id']}",
            auth=self.auth(),
        )

        self.assertEqual(response.status_code, 409)

    def test_delete_empty_category(self):
        category = self.create_category()

        response = client.delete(
            f"/admin/categories/{category['id']}",
            auth=self.auth(),
        )

        self.assertEqual(response.status_code, 200)

    def test_unknown_category_returns_404(self):
        response = client.delete(
            "/admin/categories/99999999",
            auth=self.auth(),
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
