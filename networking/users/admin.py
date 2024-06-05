"""
Django admin customizations.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User,
    FriendRequest
)


class UserAdmin(BaseUserAdmin):
    """User admin"""
    ordering = ['id']
    list_display = [
        'id',
        'name',
        'email',
        'is_staff',
    ]
    fieldsets = (
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
                    "friends"
                )
            }
        ),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'date_modified')
        })
    )
    add_fieldsets = (
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
    )
    readonly_fields = (
        'last_login', 'date_joined', 'date_modified'
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
        "friends"
    )
    search_fields = ("email", "name")
    list_editable = ('name',)


class FriendRequestAdmin(admin.ModelAdmin):
    """Friend request admin"""
    ordering = ['id']
    list_display = [
        'id',
        'sender',
        'receiver',
        'status',
        'created_at',
        'updated_at'
    ]
    list_filter = ['status']
    search_fields = ['sender__name', 'receiver__name']


admin.site.register(User, UserAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
