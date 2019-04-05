import unittest
from flask_testing import TestCase
from flask_pymongo import PyMongo
from server import app
import json

class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('config.TestConfig')

        return app

    def setUp(self):
        mongo = PyMongo(app)

        db_users = mongo.db.users
        db_movies = mongo.db.movies

        db_users.insert_many([
            {
                "name": "User 1",
                "email": "user1@example.com",
                "password": "pbkdf2:sha256:150000$p5dZtdqp$43bf3a86d5e446f3a2e0776ae6a66a803a6b1db98d5e7f9ccbb15f80130e831e"
            },
            {
                "name": "User 2",
                "email": "user2@example.com",
                "password": "pbkdf2:sha256:150000$V40F3x1W$59dea361359caadc9f7f3a27c199bdeddefb46cdb7bb794cdfef6b22616f2089"
            },
        ])

        db_movies.insert_many([
            {
                "title": "Fight Club",
                "brazilian_title": "Clube da Luta",
                "year_of_production": 1999,
                "director": "David Fincher",
                "genre": "Drama",
                "cast": [
                    {
                        "role": "Narrator",
                        "name": "Edward Norton"
                    },
                    {
                        "role": "Tyler Durden",
                        "name": "Brad Pitt"
                    }
                ]
            },
            {
                "title": "City of God",
                "brazilian_title": "Cidade de Deus",
                "year_of_production": 2002,
                "director": "Fernando Meirelles",
                "genre": "Crime",
                "cast": [
                    {
                        "role": "Zé Pequeno",
                        "name": "Leandro Firmino"
                    },
                    {
                        "role": "Angélica",
                        "name": "Alice Braga"
                    }
                ]
            }
        ])

    def tearDown(self):
        mongo = PyMongo(app)

        db_users = mongo.db.users
        db_movies = mongo.db.movies

        db_users.drop()
        db_movies.drop()

class AppTestCase(BaseTestCase):

    def test_api(self):
        response = self.client.get('/api', content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get('message', None), 'Welcome to Movies APIs')

    def test_login(self):
        # Login success
        response1 = self.client.post(
            '/api/login',
            data=json.dumps({
                'email': 'user1@example.com',
                'password': 'secret'
            }),
            content_type="application/json"
        )

        self.assertEqual(response1.status_code, 200)
        self.assertTrue(response1.json.get('access_token', None))

        # Login error - wrong password
        response2 = self.client.post(
            '/api/login',
            data=json.dumps({
                'email': 'user1@example.com',
                'password': 'secret_wrong'
            }),
            content_type="application/json"
        )

        self.assertEqual(response2.status_code, 401)

        # Login error - missing data
        response3 = self.client.post(
            '/api/login',
            data=json.dumps({}),
            content_type="application/json"
        )

        self.assertEqual(response3.status_code, 422)

    # def test_list(self):
    #     response1 = self.client.post(
    #         '/api/login',
    #         data=json.dumps({
    #             'email': 'user1@example.com',
    #             'password': 'secret2'
    #         }),
    #         content_type="application/json"
    #     )

    #     token = response1.json.get('access_token', None)

    #     # Correct Authorizarion
    #     response2 = self.client.get(
    #         '/api/movies',
    #         headers={'Authorization': 'Bearer ' + token },
    #         content_type="application/json")
        
    #     self.assertEqual(response2.status_code, 200)
    #     self.assertTrue(response2.json.get('movies', None))

    #     # Missing Authorizarion
    #     response3 = self.client.get(
    #         '/api/movies',
    #         content_type="application/json")
        
    #     self.assertEqual(response3.status_code, 401)
    #     self.assertEqual(response3.json.get('msg', None), 'Missing Authorization Header')

    #     # Incorrect Authorizarion
    #     response3 = self.client.get(
    #         '/api/movies',
    #         headers={'Authorization': 'Bearer 123456' },
    #         content_type="application/json")
        
    #     self.assertEqual(response3.status_code, 422)

if __name__ == '__main__':
    unittest.main()