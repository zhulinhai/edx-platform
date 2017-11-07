#!/usr/bin/env python
# -*- coding: utf-8 -*-
from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import translation

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from student.forms import AccountCreationForm
from student.models import CourseEnrollment, create_comments_service_user
from student.views import _do_create_account, AccountValidationError
from track.management.tracked_command import TrackedCommand

from django.utils.encoding import smart_str
import csv

class Command(TrackedCommand):
    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    metavar='COURSE_ID',
                    dest='course',
                    default=None,
                    help='course to enroll the user in (optional)'),
    )

    def handle(self, *args, **options):
        #EMAI
        with open('lista_estudiantes_espol1.csv', 'rb') as csvfile:
            for row in csv.reader(csvfile, delimiter=','):
                email = row[0]
                username = email.split('@')[0]

                try:
                    user = User.objects.get(username=username)
                    user.delete()
                    print "ya se elimino el usuario %s" % user
                except User.DoesNotExist:
                    print "No existe el usuario (%s)" % username