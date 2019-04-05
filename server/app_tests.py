from server import app
import unittest
import json

class AppTestCase(unittest.TestCase):

    def test_api(self):
        tester = app.test_client(self)
        
        response = tester.get('/api', content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get('message', None), 'Welcome to Movies APIs')

    def test_login(self):
        tester = app.test_client(self)
        
        # Login success
        response1 = tester.post(
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
        response2 = tester.post(
            '/api/login',
            data=json.dumps({
                'email': 'user1@example.com',
                'password': 'secret_wrong'
            }),
            content_type="application/json"
        )

        self.assertEqual(response2.status_code, 401)

        # Login error - missing data
        response3 = tester.post(
            '/api/login',
            data=json.dumps({}),
            content_type="application/json"
        )

        self.assertEqual(response3.status_code, 422)

    def test_list(self):
        tester = app.test_client(self)

        response1 = tester.post(
            '/api/login',
            data=json.dumps({
                'email': 'user1@example.com',
                'password': 'secret'
            }),
            content_type="application/json"
        )

        token = response1.json.get('access_token', None)

        # Correct Authorizarion
        response2 = tester.get(
            '/api/movies',
            headers={'Authorization': 'Bearer ' + token },
            content_type="application/json")
        
        self.assertEqual(response2.status_code, 200)
        self.assertTrue(response2.json.get('movies', None))

        # Missing Authorizarion
        response3 = tester.get(
            '/api/movies',
            content_type="application/json")
        
        self.assertEqual(response3.status_code, 401)
        self.assertEqual(response3.json.get('msg', None), 'Missing Authorization Header')

        # Incorrect Authorizarion
        response3 = tester.get(
            '/api/movies',
            headers={'Authorization': 'Bearer 123456' },
            content_type="application/json")
        
        self.assertEqual(response3.status_code, 422)

if __name__ == '__main__':
    unittest.main()