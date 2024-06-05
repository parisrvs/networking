""" This module contains the serializers for the users app."""
import re
from rest_framework import serializers
from .models import User


class RegisterUserSerializer(serializers.ModelSerializer):
    """
    This serializer is used to validate the data for creating a new user.
    """
    confirm_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        """ Meta class for the UserSerializer."""
        model = User
        fields = ['name', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True}
        }

    def validate(self, attrs):
        """ Validate the data for creating a new user. """
        if not attrs['password'] or not re.match(
            r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$",
            attrs['password']
        ):
            raise serializers.ValidationError(
                [
                    'User must have a valid password',
                    'password must contain at least 8 characters',
                    'at least one alphabetical character',
                    'at least one digit',
                    'and at least one special character',
                ]
            )

        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")

        if not attrs['email']:
            raise ValueError('User must have an email address')

        if not re.match(
            r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            attrs['email']
        ):
            raise ValueError('User must have a valid email address')

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RegisterUserResponseSerializer(serializers.Serializer):  # noqa  # pylint: disable=abstract-method
    """ Serializer for the response message after registering a user."""
    message = serializers.CharField()


class RegisterUserErrorSerializer(serializers.Serializer):  # noqa  # pylint: disable=abstract-method
    """ Serializer for the error message after registering a user."""
    non_field_errors = serializers.ListField(child=serializers.CharField())
    email = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    password = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    confirm_password = serializers.ListField(
        child=serializers.CharField(), required=False
    )


class LoginUserSerializer(serializers.Serializer):  # noqa  # pylint: disable=abstract-method
    """ Serializer for the login of a user."""
    email = serializers.EmailField()
    password = serializers.CharField()


class LoginUserResponseSerializer(serializers.Serializer):  # noqa  # pylint: disable=abstract-method
    """ Serializer for the response message after logging in a user. """
    message = serializers.CharField()
    token = serializers.CharField()


class LoginUserErrorSerializer(serializers.Serializer):  # noqa  # pylint: disable=abstract-method
    """ Serializer for the error message after logging in a user. """
    message = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the user model. """
    class Meta:
        """ Meta class for the UserSerializer. """
        model = User
        fields = ['name', 'email']
