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
        mode = 'honor'
        if options['course']:
            course_key = options['course']

        #EMAIL,CLAVE,CEDULA,NOMBRES,APELLIDOS
        with open('lista_estudiantes_pre_83.csv', 'rb') as csvfile:
            for row in csv.reader(csvfile, delimiter=','):
                email = row[0]
                password = row[1]
                username = row[2]
                name = smart_str(row[3]) + " " +  smart_str(row[4])

                print "Empezamos con el usuario %s (%s)" % (name, username)

                try:
                    course = CourseKey.from_string(course_key)
                # if it's not a new-style course key, parse it from an old-style
                # course key
                except InvalidKeyError:
                    course = SlashSeparatedCourseKey.from_deprecated_string(course_key)

                try:
                    user = User.objects.get(username=username)
                    print "ya existe el usuario %s" % user

                except User.DoesNotExist:
                
                    form = AccountCreationForm(
                        data={
                            'username': username,
                            'email': email,
                            'password': password,
                            'name': name,
                        },
                        tos_required=False
                    )
                    # django.utils.translation.get_language() will be used to set the new
                    # user's preferred language.  This line ensures that the result will
                    # match this installation's default locale.  Otherwise, inside a
                    # management command, it will always return "en-us".
                    translation.activate(settings.LANGUAGE_CODE)
                    try:
                        user, _, reg = _do_create_account(form)
                        reg.activate()
                        reg.save()
                        create_comments_service_user(user)
                        print "creado el usuario %s" % user
                    except AccountValidationError as e:
                        print e.message
                        user = User.objects.get(username=username)
                    translation.deactivate()

                CourseEnrollment.enroll(user, course, mode=mode)
                print "Enrolado el usuario %s en el curso %s" % (name, course)

