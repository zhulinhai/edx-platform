"""
Defines the URL routes for this app.
"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import TeamsDashboardView, TeamsRocketChatView

urlpatterns = [
    url(r"^$", login_required(TeamsDashboardView.as_view()), name="teams_dashboard"),
    url(r"^rocket-chat-discussion", login_required(TeamsRocketChatView.as_view()), name="teams_rocket_chat_discussion")
]
