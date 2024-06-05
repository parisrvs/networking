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

    friends = models.ManyToManyField(
        'self',
        blank=True
    )

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


class FriendRequest(models.Model):
    """ Friend request model """

    class RequestStatus(models.TextChoices):
        """ Request status choices """
        PENDING = 'P', _('Pending')
        ACCEPTED = 'A', _('Accepted')
        REJECTED = 'R', _('Rejected')

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_requests'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_requests'
    )
    status = models.CharField(
        max_length=1,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING
    )

    class Meta:
        """ Meta class for friend request model """
        db_table = 'friend_requests'
        verbose_name = _('Friend Request')
        verbose_name_plural = _('Friend Requests')
        unique_together = ('sender', 'receiver')
        ordering = ['sender', 'receiver']
