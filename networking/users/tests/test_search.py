from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserSearchViewTest(APITestCase):
    """ Tests for the UserSearchView """
    @classmethod
    def setUpTestData(cls):
        # Create some users for testing
        User.objects.create_user(
            email='test1@example.com',
            name='Test User 1',
            password='test@1234'
        )

        User.objects.create_user(
            email='test2@example.com',
            name='Test User 2',
            password='test@1234'
        )

        User.objects.create_user(
            email='test3@example.com',
            name='Test User 3',
            password='test@1234'
        )

        User.objects.create_user(
            email='test4@example.com',
            name='Test User 4',
            password='test@1234'
        )

        User.objects.create_user(
            email='test5@example.com',
            name='Test User 5',
            password='test@1234'
        )

        User.objects.create_user(
            email='test6@example.com',
            name='Test User 6',
            password='test@1234'
        )

        User.objects.create_user(
            email='test7@example.com',
            name='Test User 7',
            password='test@1234'
        )

        User.objects.create_user(
            email='test8@example.com',
            name='Test User 8',
            password='test@1234'
        )

        User.objects.create_user(
            email='test9@example.com',
            name='Test User 9',
            password='test@1234'
        )

        User.objects.create_user(
            email='test10@example.com',
            name='Test User 10',
            password='test@1234'
        )

        User.objects.create_user(
            email='test11@example.com',
            name='Test User 11',
            password='test@1234'
        )

        User.objects.create_user(
            email='test12@example.com',
            name='Test User 12',
            password='test@1234'
        )

    def setUp(self):
        # Authenticate
        self.user = User.objects.get(email='test1@example.com')
        self.client.force_authenticate(user=self.user)

    def test_search_by_email(self):
        """ Test that a user can be searched by email """
        response = self.client.get(
            reverse('users:user-search'),
            {'search': 'test2@example.com'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['email'],
            'test2@example.com'
        )

    def test_search_by_name(self):
        """ Test that a user can be searched by name """
        response = self.client.get(
            reverse('users:user-search'),
            {'search': 'Test User'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    def test_pagination(self):
        """ Test that the search results are paginated """
        response = self.client.get(
            reverse('users:user-search'),
            {'search': 'Test User'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 12)
        self.assertEqual(len(response.data['results']), 10)
