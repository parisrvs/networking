"""User models module."""
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
        """Creates, and saves a new user"""
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

    name = models.CharField(max_length=255, blank=True, null=True)
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
