# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import ExtraInfo


class ExtraInfoAdmin(admin.ModelAdmin):
    """
    Admin interface for ExtraInfo model.
    """

    list_display = (
        'user',
        'get_email',
        'last_name',
        'first_name',
    )
    readonly_fields = (
        'user',
    )
    search_fields = (
        'user__username',
        'user__email',
        'last_name',
        'first_name',
    )

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email address'

    class Meta(object):
        model = ExtraInfo

admin.site.register(ExtraInfo, ExtraInfoAdmin)
