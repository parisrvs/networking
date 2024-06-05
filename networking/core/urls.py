"""url conf for the core app"""

from django.urls import path
from .views import homepage

app_name = 'core'  # pylint: disable=invalid-name

urlpatterns = [
    path('', homepage, name='homepage')
]
