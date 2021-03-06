import unittest
from flask_testing import TestCase
from server import app, mongo
from bson import ObjectId
import json

class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('config.TestConfig')

        return app

    def setUp(self):
        mongo.db.users.insert_many([
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

        mongo.db.movies.insert_many([
            {
                "_id": ObjectId("5ca6a020d7d19372e81c582c"),
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
                "_id": ObjectId("5ca6fb4ad7d19356d533183f"),
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
        mongo.db.users.drop()
        mongo.db.movies.drop()

class AppTestCase(BaseTestCase):
    token = None

    def setToken(self):
        response = self.client.post(
            '/api/login',
            data=json.dumps({
                'email': 'user1@example.com',
                'password': 'secret'
            }),
            content_type="application/json"
        )

        self.token = response.json.get('access_token', None)
    
    def checkAuth(self, method, url):
        # Missing Authorizarion
        response1 = getattr(self.client, method)(
            url,
            content_type="application/json"
        )
        
        self.assertEqual(response1.status_code, 401)
        self.assertEqual(response1.json.get('msg', None), 'Missing Authorization Header')

        # Incorrect Authorizarion
        response2 = getattr(self.client, method)(
            url,
            headers={'Authorization': 'Bearer 123456' },
            content_type="application/json")
        
        self.assertEqual(response2.status_code, 422)

    def test_api(self):
        response = self.client.get('/api', content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get('message', None), 'Welcome to Movies APIs')
    
    def test_register(self):
        # Register success
        response1 = self.client.post(
            '/api/register',
            data=json.dumps({
                'name': 'User 3',
                'email': 'user3@example.com',
                'password': 'secret'
            }),
            content_type="application/json"
        )

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response1.json.get('message', None), 'User created')

        # Register duplicate
        response2 = self.client.post(
            '/api/register',
            data=json.dumps({
                'name': 'User 1',
                'email': 'user1@example.com',
                'password': 'secret'
            }),
            content_type="application/json"
        )

        self.assertEqual(response2.status_code, 409)
        self.assertEqual(response2.json.get('message', None), 'Duplicate email \'user1@example.com\'')

        # Register missing data
        response3 = self.client.post(
            '/api/register',
            content_type="application/json"
        )
        
        self.assertEqual(response3.status_code, 422)
        self.assertEqual(response3.json.get('message', None), 'Invalid parameters')

        # Register invalid data
        response4 = self.client.post(
            '/api/register',
            data=json.dumps({
                'name': 'User 1',
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response4.status_code, 422)
        self.assertEqual(response4.json.get('message', None), 'Invalid parameters')

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

    def test_list(self):
        method = 'get'
        url = 'api/movies'

        self.setToken()
        self.checkAuth(method, url)

        # Correct Authorizarion
        response1 = getattr(self.client, method)(
            url,
            headers={ 'Authorization': 'Bearer ' + self.token },
            content_type="application/json"
        )
        
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(response1.json.get('movies', None))

    def test_show(self):
        method = 'get'
        url = 'api/movies/5ca6a020d7d19372e81c582c'

        self.setToken()
        self.checkAuth(method, url)

        # Correct Authorizarion and movie_id
        response1 = getattr(self.client, method)(
            url,
            headers={ 'Authorization': 'Bearer ' + self.token },
            content_type="application/json"
        )
        
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(response1.json.get('item', None))

        # Correct Authorizarion, invalid movie_id
        response2 = getattr(self.client, method)(
            '/api/movies/123456',
            headers={ 'Authorization': 'Bearer ' + self.token },
            content_type="application/json"
        )
        
        self.assertEqual(response2.status_code, 422)
        self.assertEqual(response2.json.get('message', None), 'Invalid parameters')

        # Correct Authorizarion, incorrect movie_id
        response3 = getattr(self.client, method)(
            '/api/movies/507f191e810c19729de860ea',
            headers={ 'Authorization': 'Bearer ' + self.token },
            content_type="application/json"
        )
        
        self.assertEqual(response3.status_code, 404)
        self.assertEqual(response3.json.get('message', None), 'Movie not found')

    def test_create(self):
        method = 'post'
        url = '/api/movies'

        self.setToken()
        self.checkAuth(method, url)

        # Correct Authorizarion and movie
        response1 = getattr(self.client, method)(
            url,
            headers={'Authorization': 'Bearer ' + self.token },
            data=json.dumps({
                "title": "Get Out",
                "brazilian_title": "Corra!",
                "year_of_production": 2017,
                "director": "Jordan Peele",
                "genre": "Horror",
                "cast": [
                    {
                        "role": "Chris Washington",
                        "name": "Daniel Kaluuya"
                    },
                    {
                        "role": "Rose Armitage",
                        "name": "Allison Williams"
                    }
                ]
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response1.json.get('message', None), 'Movie created')

        # Correct Authorizarion, duplicate movie title
        response2 = getattr(self.client, method)(
            url,
            headers={ 'Authorization': 'Bearer ' + self.token },
            data=json.dumps({
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
            }),
            content_type="application/json")
        
        self.assertEqual(response2.status_code, 409)
        self.assertEqual(response2.json.get('message', None), 'Duplicate title \'City of God\'')

        # Correct Authorizarion, incorrect movie data
        response3 = getattr(self.client, method)(
            '/api/movies',
            headers={ 'Authorization': 'Bearer ' + self.token },
            data=json.dumps({
                "title": "Get Out",
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response3.status_code, 422)
        self.assertEqual(response3.json.get('message', None), 'Invalid parameters')

        # Invalid cast
        response4 = getattr(self.client, method)(
            url,
            headers={ 'Authorization': 'Bearer ' + self.token },
            data=json.dumps({
                "title": "Get Out",
                "brazilian_title": "Corra!",
                "year_of_production": 2017,
                "director": "Jordan Peele",
                "genre": "Horror",
                "cast": [
                    {
                        "role": "Chris Washington",
                    },
                    {
                        "role": "Rose Armitage",
                        "name": "Allison Williams"
                    }
                ]
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response4.status_code, 422)
        self.assertEqual(response4.json.get('message', None), 'Invalid parameters')

    def test_update(self):
        method = 'put'
        url = 'api/movies/5ca6a020d7d19372e81c582c'

        self.setToken()
        self.checkAuth(method, url)

        # Correct Authorizarion, movie_id and data
        response1 = getattr(self.client, method)(
            url,
            headers={ 'Authorization': 'Bearer ' + self.token },
            data=json.dumps({
                'year_of_production': 2000,
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.json.get('message', None), 'Movie updated')

        # Correct Authorizarion, movie_id, empty data
        response2 = getattr(self.client, method)(
            url,
            headers={ 'Authorization': 'Bearer ' + self.token },
            data=json.dumps({}),
            content_type="application/json"
        )
        
        self.assertEqual(response2.status_code, 422)
        self.assertEqual(response2.json.get('message', None), 'Invalid parameters')

        # Correct Authorizarion, movie_id, missing data
        response3 = getattr(self.client, method)(
            url,
            headers={ 'Authorization': 'Bearer ' + self.token },
            content_type="application/json"
        )
        
        self.assertEqual(response3.status_code, 422)
        self.assertEqual(response3.json.get('message', None), 'Invalid parameters')

        # Correct Authorizarion, invalid movie_id
        response4 = getattr(self.client, method)(
            '/api/movies/123456',
            headers={ 'Authorization': 'Bearer ' + self.token },
            data=json.dumps({
                'year_of_production': 2000,
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response4.status_code, 422)
        self.assertEqual(response4.json.get('message', None), 'Invalid parameters')

        # Correct Authorizarion, incorrect movie_id
        response5 = getattr(self.client, method)(
            '/api/movies/507f191e810c19729de860ea',
            headers={ 'Authorization': 'Bearer ' + self.token },
            data=json.dumps({
                'year_of_production': 2000,
            }),
            content_type="application/json")
        
        self.assertEqual(response5.status_code, 404)
        self.assertEqual(response5.json.get('message', None), 'Movie not found')

    def test_delete(self):
        method = 'delete'
        url = 'api/movies/5ca6a020d7d19372e81c582c'

        self.setToken()
        self.checkAuth(method, url)

        # Correct Authorizarion and movie_id
        response1 = getattr(self.client, method)(
            url,
            headers={ 'Authorization': 'Bearer ' + self.token },
            content_type="application/json"
        )
        
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(response1.json.get('item', None))

        # Correct Authorizarion, invalid movie_id
        response2 = getattr(self.client, method)(
            '/api/movies/123456',
            headers={ 'Authorization': 'Bearer ' + self.token },
            content_type="application/json"
        )
        
        self.assertEqual(response2.status_code, 422)
        self.assertEqual(response2.json.get('message', None), 'Invalid parameters')

        # Correct Authorizarion, incorrect movie_id
        response3 = getattr(self.client, method)(
            '/api/movies/507f191e810c19729de860ea',
            headers={ 'Authorization': 'Bearer ' + self.token },
            content_type="application/json"
        )
        
        self.assertEqual(response3.status_code, 404)
        self.assertEqual(response3.json.get('message', None), 'Movie not found')

if __name__ == '__main__':
    unittest.main()