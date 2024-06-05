""" Tests for the friend request endpoints """
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import FriendRequest

User = get_user_model()


class FriendRequestViewTest(APITestCase):
    """ Tests for the FriendRequestView """

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='pass@1234')
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='pass@1234')
        self.url = reverse('users:friend-request')

    def test_send_friend_request(self):
        """ Test sending a friend request """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, {'receiver_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # pylint: disable=no-member
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_send_friend_request_to_self(self):
        """ Test sending a friend request to self """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, {'receiver_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'You cannot send a friend request to yourself',
            response.data['message']
        )

    def test_send_friend_request_to_nonexistent_user(self):
        """ Test sending a friend request to a nonexistent user"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.url, {'receiver_id': 999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('User not found', response.data['message'])

    def test_send_duplicate_friend_request(self):
        """ Test sending a duplicate friend request """
        self.client.force_authenticate(user=self.user1)
        self.client.post(self.url, {'receiver_id': self.user2.id})
        response = self.client.post(self.url, {'receiver_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Friend request already sent', response.data['message'])

    def test_send_friend_request_to_friend(self):
        """ Test sending a friend request to a friend """
        self.client.force_authenticate(user=self.user1)
        self.client.post(self.url, {'receiver_id': self.user2.id})

        # change pending request to accepted
        #  pylint: disable=no-member
        friend_request = FriendRequest.objects.get(
            sender=self.user1,
            receiver=self.user2
        )
        friend_request.status = FriendRequest.RequestStatus.ACCEPTED
        friend_request.save()

        response = self.client.post(self.url, {'receiver_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You are already friends', response.data['message'])

    def test_send_friend_request_to_rejected(self):
        """ Test sending a friend request to a rejected request """
        self.client.force_authenticate(user=self.user1)
        self.client.post(self.url, {'receiver_id': self.user2.id})

        # change pending request to rejected
        #  pylint: disable=no-member
        friend_request = FriendRequest.objects.get(
            sender=self.user1,
            receiver=self.user2
        )
        friend_request.status = FriendRequest.RequestStatus.REJECTED
        friend_request.save()

        response = self.client.post(self.url, {'receiver_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Friend request rejected', response.data['message'])


class AcceptRejectFriendRequestViewTest(APITestCase):
    """ Tests for the AcceptRejectFriendRequestView """

    def setUp(self):
        self.sender = User.objects.create_user(
            email='user1@example.com',
            password='pass@1234'
        )
        self.receiver = User.objects.create_user(
            email='user2@example.com',
            password='pass@1234'
        )

        # pylint: disable=no-member
        self.friend_request = FriendRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver
        )

        self.url = reverse(
            'users:accept-reject-friend-request',
            args=[self.sender.id]
        )

    def test_accept_friend_request(self):
        """ Test accepting a friend request """
        self.client.force_authenticate(user=self.receiver)
        response = self.client.post(self.url, {'action': 'accept'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.receiver, list(self.sender.friends.all()))
        self.assertIn(self.sender, list(self.receiver.friends.all()))
        self.assertEqual(response.data['message'], 'Friend request accepted')

    def test_reject_friend_request(self):
        """ Test rejecting a friend request """
        self.client.force_authenticate(user=self.receiver)
        response = self.client.post(self.url, {'action': 'reject'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.receiver, list(self.sender.friends.all()))
        self.assertNotIn(self.sender, list(self.receiver.friends.all()))
        self.assertEqual(response.data['message'], 'Friend request rejected')

    def test_accept_nonexistent_user(self):
        """ Test accepting a nonexistent friend request """
        url = reverse('users:accept-reject-friend-request', args=[999])
        self.client.force_authenticate(user=self.receiver)
        response = self.client.post(url, {'action': 'accept'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('User not found', response.data['message'])

    def test_accept_nonexistent_friend_request(self):
        """ Test accepting a nonexistent friend request """
        # pylint: disable=no-member
        self.friend_request.delete()
        self.client.force_authenticate(user=self.receiver)
        response = self.client.post(self.url, {'action': 'accept'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Friend request not found', response.data['message'])

    def test_accept_friend_request_with_invalid_action(self):
        """ Test accepting a friend request with an invalid action """
        self.client.force_authenticate(user=self.receiver)
        response = self.client.post(self.url, {'action': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid action', response.data['message'])


class ListFriendsViewTest(APITestCase):
    """ Tests for the ListFriendsView """

    def setUp(self):
        self.user = User.objects.create_user(
            email='user1@example.com',
            password='pass@1234'
        )

        self.friend1 = User.objects.create_user(
            email='friend1@example.com',
            password='pass@1234'
        )

        self.friend2 = User.objects.create_user(
            email='friend2@example.com',
            password='pass@1234'
        )

        self.user_anonymous = User.objects.create_user(
            email='someone@example.com',
            password='pass@1234'
        )

        self.user.friends.add(self.friend1)
        self.user.friends.add(self.friend2)

        self.url = reverse('users:friends')

    def test_list_friends(self):
        """ Test listing friends """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(
            response.data["results"][0]['email'],
            'friend1@example.com'
        )
        self.assertEqual(
            response.data["results"][1]['email'],
            'friend2@example.com'
        )

    def test_list_friends_symetrical(self):
        """ Test listing friends symetrical relationship """
        self.client.force_authenticate(user=self.friend1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]['email'],
            'user1@example.com'
        )

    def test_list_friends_empty(self):
        """ Test listing friends with no friends """
        self.client.force_authenticate(user=self.user_anonymous)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)


class ListPendingRequestsViewtest(APITestCase):
    """ Tests for the ListPendingRequestsView """

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='pass@1234'
        )

        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='pass@1234'
        )

        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='pass@1234'
        )

        self.user3 = User.objects.create_user(
            email='user3@example.com',
            password='pass@1234'
        )

        self.user4 = User.objects.create_user(
            email='user4@example.com',
            password='pass@1234'
        )

        # pylint: disable=no-member
        FriendRequest.objects.create(
            sender=self.user1,
            receiver=self.user
        )

        FriendRequest.objects.create(
            sender=self.user2,
            receiver=self.user,
            status=FriendRequest.RequestStatus.ACCEPTED
        )

        FriendRequest.objects.create(
            sender=self.user3,
            receiver=self.user,
            status=FriendRequest.RequestStatus.REJECTED
        )

        FriendRequest.objects.create(
            sender=self.user4,
            receiver=self.user
        )

        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:pending-requests')

    def test_list_pending_requests(self):
        """ Test listing pending requests """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(
            response.data["results"][0]['email'],
            'user1@example.com'
        )
        self.assertEqual(
            response.data["results"][1]['email'],
            'user4@example.com'
        )
