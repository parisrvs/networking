""" This file contains the views for the users app. """
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import (
    viewsets,
    permissions,
    response,
    status,
    generics,
    pagination
)
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)
from .models import User, FriendRequest
from .serializers import (
    RegisterUserSerializer,
    RegisterUserResponseSerializer,
    RegisterUserErrorSerializer,
    LoginUserSerializer,
    LoginUserResponseSerializer,
    LoginUserErrorSerializer,
    FriendRequestResponseSerializer,
    FriendRequestErrorSerializer,

    UserSerializer,
    FriendRequestSerializer
)


class TenPerPagePagination(pagination.PageNumberPagination):
    """ This class sets the number of items per page. """
    page_size = 10


@extend_schema(
    request=RegisterUserSerializer,
    responses={
        201: RegisterUserResponseSerializer,
        400: RegisterUserErrorSerializer
    }
)
class RegisterView(viewsets.ViewSet):
    """ This view handles the registration of users. """
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post']

    def post(self, request):
        """ Registers a new user. """
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                {'message': 'User registered successfully'},
                status=status.HTTP_201_CREATED
            )

        return response.Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    request=LoginUserSerializer,
    responses={
        200: LoginUserResponseSerializer,
        400: LoginUserErrorSerializer
    }
)
class LoginView(viewsets.ViewSet):
    """ This view handles the login of users. """
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post']

    def post(self, request):
        """ Logs in a user. """
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:  # pylint: disable=no-member
            return response.Response(
                {'message': 'Invalid email address.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.check_password(password):
            # pylint: disable=no-member
            token, _ = Token.objects.get_or_create(user=user)
            return response.Response(
                {'message': 'Login successful', 'token': token.key},
                status=status.HTTP_200_OK
            )

        return response.Response(
            {'message': 'Invalid password.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search users by email or name",
            required=True,
        )
    ],
    responses={200: UserSerializer(many=True)},
)
class UserSearchView(generics.ListAPIView):
    """ This view handles the search of users. """
    serializer_class = UserSerializer
    pagination_class = TenPerPagePagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_param = self.request.query_params.get('search', '')
        return User.objects.filter(
            Q(email=search_param) | Q(name__icontains=search_param)
        )


@extend_schema(
    request=FriendRequestSerializer,
    responses={
        201: FriendRequestResponseSerializer,
        400: FriendRequestErrorSerializer
    }
)
class FriendRequestView(viewsets.ViewSet):
    """ This view handles the sending of friend requests."""
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']

    def post(self, request):
        """ Sends a friend request."""
        # Check if user has sent more than 3 friend requests in the last minute
        one_minute_ago = timezone.now() - timedelta(minutes=1)

        #  pylint: disable=no-member
        recent_requests = FriendRequest.objects.filter(
            sender=request.user,
            created_at__gte=one_minute_ago
        ).count()
        if recent_requests >= 3:
            return response.Response(
                {'message': 'Too many requests.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        receiver_id = request.data.get('receiver_id')
        try:
            receiver_id = int(receiver_id)
            assert User.objects.filter(id=receiver_id).exists()
        except (ValueError, AssertionError):
            return response.Response(
                {'message': 'User not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if receiver_id == request.user.id:
            return response.Response(
                {'message': 'You cannot send a friend request to yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if FriendRequest.objects.filter(  # pylint: disable=no-member
            sender=request.user,
            receiver_id=receiver_id,
            status=FriendRequest.RequestStatus.PENDING
        ).exists():
            return response.Response(
                {'message': 'Friend request already sent'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if FriendRequest.objects.filter(  # pylint: disable=no-member
            sender=request.user,
            receiver_id=receiver_id,
            status=FriendRequest.RequestStatus.ACCEPTED
        ).exists():
            return response.Response(
                {'message': 'You are already friends'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if FriendRequest.objects.filter(  # pylint: disable=no-member
            sender=request.user,
            receiver_id=receiver_id,
            status=FriendRequest.RequestStatus.REJECTED
        ).exists():
            return response.Response(
                {'message': 'Friend request rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        friend_request = FriendRequest(
            sender=request.user,
            receiver_id=receiver_id
        )
        friend_request.save()

        return response.Response(
            {'message': 'Friend request sent'},
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='action',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Accept or reject a friend request',
            enum=['accept', 'reject'],
            required=True
        )
    ],
    responses={
        200: FriendRequestResponseSerializer,
        400: FriendRequestErrorSerializer
    }
)
class AcceptRejectFriendRequestView(viewsets.ViewSet):
    """ This view handles the acceptance or rejection of friend requests."""
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, sender_id):
        """ Accepts or rejects a friend request."""
        # pylint: disable=no-member
        try:
            sender_id = int(sender_id)
            assert User.objects.filter(id=sender_id).exists()
        except (ValueError, AssertionError):
            return response.Response(
                {'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            assert FriendRequest.objects.filter(
                sender_id=sender_id,
                receiver=request.user
            ).exists()
        except AssertionError:
            return response.Response(
                {'message': 'Friend request not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        action = request.data.get('action')
        if action == 'accept':
            friend_request = FriendRequest.objects.get(
                sender_id=sender_id,
                receiver=request.user
            )

            if friend_request.status != FriendRequest.RequestStatus.PENDING:
                return response.Response(
                    {'message': 'Friend request already accepted or rejected'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            friend_request.status = FriendRequest.RequestStatus.ACCEPTED
            friend_request.save()

            friend_request.sender.friends.add(friend_request.receiver)
            friend_request.receiver.friends.add(friend_request.sender)

            return response.Response(
                {'message': 'Friend request accepted'},
                status=status.HTTP_200_OK
            )
        elif action == 'reject':
            friend_request = FriendRequest.objects.get(
                sender_id=sender_id,
                receiver=request.user
            )

            if friend_request.status != FriendRequest.RequestStatus.PENDING:
                return response.Response(
                    {'message': 'Friend request already accepted or rejected'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            friend_request.status = FriendRequest.RequestStatus.REJECTED
            friend_request.save()

            return response.Response(
                {'message': 'Friend request rejected'},
                status=status.HTTP_200_OK
            )
        else:
            return response.Response(
                {'message': 'Invalid action'},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
    responses={200: UserSerializer(many=True)}
)
class ListFriendsView(generics.ListAPIView):
    """ This view lists all friends of a user. """
    serializer_class = UserSerializer
    pagination_class = TenPerPagePagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ Get the friends of the user. """
        return self.request.user.friends.all()


@extend_schema(
    responses={200: UserSerializer(many=True)}
)
class ListPendingRequestsView(generics.ListAPIView):
    """ This view lists all pending friend requests of a user. """
    serializer_class = UserSerializer
    pagination_class = TenPerPagePagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ Get the pending friend requests of the user. """
        # pylint: disable=no-member
        pending_requests = FriendRequest.objects.filter(
            receiver=self.request.user,
            status=FriendRequest.RequestStatus.PENDING
        ).values_list('sender_id', flat=True)

        return User.objects.filter(id__in=pending_requests)
