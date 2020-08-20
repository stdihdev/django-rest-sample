import json
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

class SignupTests(APITestCase):
    def test_create_account(self):
        url = reverse('signup')
        data = {
            'first_name': 'Hideo',
            'last_name': 'Suzuki',
            'username': 'hideo',
            'email': 'hideo@suzuki.com',
            'password': 'password',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class LoginTests(APITestCase):
    url = reverse('login')

    def setUp(self):
        url = reverse('signup')
        data = {
            'first_name': 'Hideo',
            'last_name': 'Suzuki',
            'username': 'hideo',
            'email': 'hideo@suzuki.com',
            'password': 'password',            
        }
        self.client.post(url, data, format='json')

    def test_login_with_wrong_password(self):
        response = self.client.post(self.url, {'username': 'hideo', 'password': 'wrong password'})
        self.assertEqual(400, response.status_code)

    def test_login_with_correct_credentials(self):
        response = self.client.post(self.url, {'username': 'hideo', 'password': 'password'})
        self.assertEqual(200, response.status_code)
        self.assertTrue('token' in json.loads(response.content))
