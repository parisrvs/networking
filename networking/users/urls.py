""" This module contains the urls for the users app. """
from django.urls import path
from . import views

app_name = 'users'  # noqa  # pylint: disable=invalid-name


urlpatterns = [
    path(
        'register/',
        views.RegisterView.as_view({'post': 'post'}),
        name='register'
    ),
    path(
        'login/',
        views.LoginView.as_view({'post': 'post'}),
        name='login'
    ),
    path(
        'search/',
        views.UserSearchView.as_view(),
        name='user-search'
    ),
    path(
        'friend-request/',
        views.FriendRequestView.as_view({'post': 'post'}),
        name='friend-request'
    ),
    path(
        'friend-request/<int:sender_id>/',
        views.AcceptRejectFriendRequestView.as_view({'post': 'post'}),
        name='accept-reject-friend-request'
    ),
    path(
        'friends/',
        views.ListFriendsView.as_view(),
        name='friends'
    ),
    path(
        'pending-requests/',
        views.ListPendingRequestsView.as_view(),
        name='pending-requests'
    ),
]
