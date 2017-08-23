# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

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


class NewUserAdmin(UserAdmin):
    """
    Modifies admin interface for User model to display additional ExtraInfo link.
    """

    def __init__(self, *args, **kwargs):
        super(NewUserAdmin, self).__init__(*args, **kwargs)
        admin.views.main.EMPTY_CHANGELIST_VALUE = ''

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'extrainfo_link',
    )
    list_select_related = (
        'extrainfo',
    )

    def extrainfo_link(self, obj):
        return format_html(
            '<a href="/admin/register_cme/extrainfo/{extrainfo_id}">ExtraInfo</a>',
            extrainfo_id=obj.extrainfo.id,
        )
    extrainfo_link.short_description = 'ExtraInfo'
    extrainfo_link.allow_tags = True


admin.site.register(ExtraInfo, ExtraInfoAdmin)
admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
