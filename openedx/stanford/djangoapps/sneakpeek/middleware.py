"""
Middleware class handling sneakpeek in cms, which should never be allowed
"""
from student.models import UserProfile
from django.contrib.auth import logout
from django.shortcuts import redirect


class SneakPeekLogoutMiddleware(object):
    """
    Log out all sneakpeek users and redirect the same URL
    """
    def process_request(self, request):
        """
        Log out all sneakpeek users and redirect the same URL
        """
        if request.user.is_anonymous():
            return None
        if UserProfile.has_registered(request.user):
            return None
        logout(request)
        return redirect(request.get_full_path())
