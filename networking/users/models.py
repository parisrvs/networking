"""User models module."""
import re
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """User manager"""

    def create_user(self, email, password=None, **extra_fields):
        """Validates, creates, and saves a new user"""
        name = extra_fields.get('name')
        if not name:
            raise ValueError('User must have a name')
        name = name.strip().lower().title()

        if not password or not re.match(
            r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$",
            password
        ):
            raise ValueError(
                [
                    'User must have a valid password',
                    'password must contain at least 8 characters',
                    'at least one alphabetical character',
                    'at least one digit',
                    'and at least one special character',
                ]
            )

        if not email:
            raise ValueError('User must have an email address')

        if not re.match(
            r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            email
        ):
            raise ValueError('User must have a valid email address')

        extra_fields['name'] = name
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Creates and saves a new superuser"""

        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports login
    using email instead of username
    """

    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return str(self.name)

    class Meta:
        """Meta class for user model"""
        ordering = ['name']
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'users'
