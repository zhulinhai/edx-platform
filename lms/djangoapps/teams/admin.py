from django.contrib import admin

from lms.djangoapps.teams.models import CourseTeamMembership, CourseTeam

admin.site.register(CourseTeamMembership)
admin.site.register(CourseTeam)
