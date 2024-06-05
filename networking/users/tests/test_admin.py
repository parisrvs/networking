"""
Tests for the Django Admin modifications.
"""

from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from users.admin import UserAdmin
from users.models import User


class MockSuperUser:
    """ Mock Super User"""
    def __init__(self, is_superuser):
        self.is_superuser = is_superuser


class UserAdminTest(TestCase):
    """ Test cases for UserAdmin class"""
    def setUp(self):
        self.site = AdminSite()
        self.admin = UserAdmin(User, self.site)

    def test_fieldsets(self):
        """ Test fieldsets"""
        fieldsets = self.admin.fieldsets
        self.assertEqual(
            fieldsets[0][1]['fields'],
            ('email', 'password', 'name')
        )
        self.assertEqual(
            fieldsets[1][1]['fields'],
            (
                'is_active',
                'is_staff',
                'is_superuser',
                "groups",
                "user_permissions",
            )
        )
        self.assertEqual(
            fieldsets[2][1]['fields'],
            ('last_login', 'date_joined', 'date_modified')
        )

    def test_add_fieldsets(self):
        """ Test add fieldsets """
        add_fieldsets = self.admin.add_fieldsets
        self.assertEqual(
            add_fieldsets[0][1]['fields'],
            ('email', 'password1', 'password2', 'name')
        )

    def test_readonly_fields(self):
        """ Test readonly fields"""
        readonly_fields = self.admin.readonly_fields
        self.assertEqual(
            readonly_fields, ('last_login', 'date_joined', 'date_modified')
        )

    def test_model_admin(self):
        """ Test model admin"""
        self.assertEqual(self.admin.model, User)
        self.assertEqual(self.admin.fieldsets, (
            (
                (
                    None, {
                        'fields': (
                            'email',
                            'password',
                            'name',
                        )
                    }
                ),
                (
                    _('Permissions'),
                    {
                        'fields': (
                            'is_active',
                            'is_staff',
                            'is_superuser',
                            "groups",
                            "user_permissions",
                        )
                    }
                ),
                (_('Important dates'), {
                    'fields': ('last_login', 'date_joined', 'date_modified')
                })
            )
        ))
        self.assertEqual(self.admin.add_fieldsets, (
            (
                None,
                {
                    'classes': ('wide',),
                    'fields': (
                        'email',
                        'password1',
                        'password2',
                        'name',
                    ),
                }
            ),
        ))
        self.assertEqual(self.admin.readonly_fields, (
            'last_login', 'date_joined', 'date_modified'
        ))


class AdminSiteTests(TestCase):
    """Test cases for admin site"""

    def setUp(self):
        """Setup function for tests"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            name="admin",
            email="admin@example.com",
            password="Abcd*1234"
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            name="user",
            email="user@example.com",
            password="Abcd*1234",
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:users_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:users_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:users_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_user_delete(self):
        """Test that the user delete works"""
        url = reverse('admin:users_user_delete', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
