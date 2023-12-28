import os
import unittest
import json
from dotenv import load_dotenv
from flaskr import create_app
from models import setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        load_dotenv()
        TEST_DB_NAME = os.environ.get('TEST_DB_NAME')
        DB_USER = os.environ.get('DB_USER')
        DB_PASSWORD = os.environ.get('DB_PASSWORD')
        DB_HOST = os.environ.get('DB_HOST')
        DB_PORT = os.environ.get('DB_PORT')
        self.database_name = TEST_DB_NAME
        self.database_path = (
            f'postgresql://{DB_USER}:{DB_PASSWORD}@'
            f'{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}'
        )

        self.app = create_app(test_config=True)
        self.client = self.app.test_client

        setup_db(self.app, self.database_path)

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for
    successful operation and for expected errors.
    """

    '''
    test /categories
    '''

    def test_get_categories_success(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(isinstance(data['categories'], dict))

    def test_get_categories_fail(self):
        response = self.client().post('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 405)
        self.assertTrue(data['message'])

    '''
    test /questions
    '''

    def test_get_questions_success(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(isinstance(data['questions'], list))
        self.assertTrue(data['categories'])
        self.assertTrue(isinstance(data['categories'], dict))
        self.assertTrue(data['currentCategory'])
        self.assertTrue(isinstance(data['currentCategory'], str))
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(isinstance(data['totalQuestions'], int))

    def test_get_questions_fail(self):
        response = self.client().patch('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 405)
        self.assertTrue(data['message'])

    '''
    test /categories/1/questions
    '''

    def test_get_questions_by_category_success(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(isinstance(data['questions'], list))
        self.assertTrue(data['currentCategory'])
        self.assertTrue(isinstance(data['currentCategory'], str))
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(isinstance(data['totalQuestions'], int))

    def test_get_questions_by_category_fail(self):
        response = self.client().get('/categories/a/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertTrue(data['message'])

    '''
    test POST /questions (create)
    '''

    def test_post_questions_success(self):
        new_question = {
            "question": "Is this test working?",
            "answer": "Yes",
            "difficulty": 5,
            "category": 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['created'])

    def test_post_questions_fail(self):
        new_question = {
            "question": "Is this test working?",
            "difficulty": 5,
            "category": 1
        }
        res = self.client().post('/questions', json=new_question)
        self.assertEqual(res.status_code, 500)

    '''
    test POST /questions (search)
    '''

    def test_search_questions_success(self):
        search_query = {
            "searchTerm": "medic"
        }
        res = self.client().post('/questions', json=search_query)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(isinstance(data['questions'], list))
        self.assertTrue(data['currentCategory'])
        self.assertTrue(isinstance(data['currentCategory'], str))
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(isinstance(data['totalQuestions'], int))

    def test_search_questions_fail(self):
        search_query = {
            "search": "medic"
        }
        res = self.client().post('/questions', json=search_query)
        self.assertEqual(res.status_code, 500)

    '''
    test DELETE /questions
    '''

    def test_delete_questions_success(self):
        new_question = {
            "question": "Is this test working?",
            "answer": "Yes",
            "difficulty": 5,
            "category": 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        question_id = data['created']

        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['deleted'])

    def test_delete_questions_fail(self):
        response = self.client().delete('/questions/a')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertTrue(data['message'])

    '''
    test POST /quizzes
    '''

    def test_quizzes_success(self):
        body = {
            "quiz_category": {
                "id": 4,
                "type": "History"
            },
            "previous_questions": []
        }
        res = self.client().post('/quizzes', json=body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertTrue(isinstance(data['question'], object))

    def test_quizzes_fail(self):
        body = {
            "previous_questions": []
        }
        res = self.client().post('/quizzes', json=body)
        self.assertEqual(res.status_code, 400)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
