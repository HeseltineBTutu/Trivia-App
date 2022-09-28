import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'postgres', 'postgres', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "Who will the premier league",
            "answer": "Manchester United",
            "category": "6",
            "difficulty": "3"}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # def test_get_categories(self):
    #     res = self.client().get('/categories')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)

    # def test_get_questions_by_category(self):
    #     res = self.client().get('/categories/1/questions')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['questions'])
    #     self.assertTrue(data['totalQuestions'])
    #     self.assertTrue(data['currentCategory'])

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data['success'])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(data["currentCategory"])

    def test_delete(self):
        question = Question(
            question='new_question',
            answer='new_answer',
            difficulty=1,
            category=1
        )
        question.insert()
        question_id = question.id

        res = self.client().delete("/questions/" + str(question_id))
        data = json.loads(res.data)

        question = Question.query.get(question_id)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNone(question)

    def test_delete_fail(self):
        res = self.client().delete("/questions/999")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["error"], 404)

    def test_create_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        question = Question.query.get(data["created"])

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(question)

    def test_search_questions_success(self):
        res = self.client().post("/questions", json={"searchTerm": "art"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])

    def test_search_questions_empty_string(self):
        res = self.client().post("/questions", json={"searchTerm": " "})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])

    def test_search_questions_not_found(self):
        res = self.client().post("/questions", json={"searchTerm": "abcdxyz"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(len(data["questions"]))
        self.assertFalse(data["totalQuestions"])

    def test_get_questions_by_category_success(self):
        res = self.client().get("/categories/4/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])

    def test_get_question_to_play(self):
        res = self.client().post("/quizzes", json={
        "previous_questions": [],
        "quiz_category": 6
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
