""" This file contains the views for the users app. """
from rest_framework import viewsets, permissions, response, status
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import (
    RegisterUserSerializer,
    RegisterUserResponseSerializer,
    RegisterUserErrorSerializer,
    LoginUserSerializer,
    LoginUserResponseSerializer,
    LoginUserErrorSerializer
)


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
