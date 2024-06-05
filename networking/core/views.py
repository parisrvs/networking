"""views for the core app"""
from django.http import HttpResponseRedirect
from django.urls import reverse


def homepage(request):  # pylint: disable=unused-argument
    """
    Redirect to the admin site
    """
    return HttpResponseRedirect(reverse('admin:index'))
