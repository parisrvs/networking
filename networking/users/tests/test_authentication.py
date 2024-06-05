""" Tests for the authentication views """
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

User = get_user_model()


class RegisterViewTest(APITestCase):
    """ Tests for the RegisterView """
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('users:register')

    def test_register_success(self):
        """ Test that a user can register successfully """
        data = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['message'],
            'User registered successfully'
        )
        self.assertTrue(User.objects.filter(email=data['email']).exists())

    def test_register_passwords_do_not_match(self):
        """ Test that passwords must match """
        data = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'Test@1234',
            'confirm_password': 'Test@12345'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'Passwords do not match',
            response.data['non_field_errors']
        )

    def test_register_invalid_email(self):
        """ Test that an invalid email is not accepted """
        data = {
            'name': 'Test User',
            'email': 'invalidemail',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Enter a valid email address.', response.data['email'])

    def test_register_invalid_password(self):
        """ Test that an invalid password is not accepted """
        data = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'invalidpassword',
            'confirm_password': 'invalidpassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'User must have a valid password',
            response.data['non_field_errors']
        )


class LoginViewTest(APITestCase):
    """ Tests for the LoginView """
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('users:login')
        self.user = User.objects.create_user(
            name='Test User',
            email='testuser@example.com',
            password='Test@1234'
        )

    def test_login_success(self):
        """ Test that a user can login successfully """
        data = {
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Login successful')
        self.assertTrue('token' in response.data)

    def test_login_invalid_email(self):
        """ Test that an invalid email is not accepted """
        data = {
            'email': 'invalidemail@example.com',
            'password': 'Test@1234'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid email address.')

    def test_login_invalid_password(self):
        """ Test that an invalid password is not accepted """
        data = {
            'email': 'testuser@example.com',
            'password': 'InvalidPassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid password.')
