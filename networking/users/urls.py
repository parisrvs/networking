"""
This module contains the urls for the users app.
1) Register a new user - POST /register/
2) Login a user - POST /login/
3) Search for a user - GET /search/
4) Send friend request - POST /friend-request/
5) Accept or reject a friend request - POST /friend-request/<int:sender_id>/
6) List friends - GET /friends/
7) List pending requests - GET /pending-requests/
"""
from django.urls import path
from . import views

app_name = 'users'  # noqa  # pylint: disable=invalid-name


urlpatterns = [
    # Register a new user
    path(
        'register/',
        views.RegisterView.as_view({'post': 'post'}),
        name='register'
    ),
    # Login a user
    path(
        'login/',
        views.LoginView.as_view({'post': 'post'}),
        name='login'
    ),
    # Search for a user
    path(
        'search/',
        views.UserSearchView.as_view(),
        name='user-search'
    ),
    # Send friend request
    path(
        'friend-request/',
        views.FriendRequestView.as_view({'post': 'post'}),
        name='friend-request'
    ),
    # Accept or reject a friend request
    path(
        'friend-request/<int:sender_id>/',
        views.AcceptRejectFriendRequestView.as_view({'post': 'post'}),
        name='accept-reject-friend-request'
    ),
    # List friends
    path(
        'friends/',
        views.ListFriendsView.as_view(),
        name='friends'
    ),
    # List pending requests
    path(
        'pending-requests/',
        views.ListPendingRequestsView.as_view(),
        name='pending-requests'
    ),
]
