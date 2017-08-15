# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import ExtraInfo


class ExtraInfoAdmin(admin.ModelAdmin):
    """
    Admin interface for ExtraInfo model.
    """

    readonly_fields = (
        'user',
    )

    class Meta(object):
        model = ExtraInfo

admin.site.register(ExtraInfo, ExtraInfoAdmin)
