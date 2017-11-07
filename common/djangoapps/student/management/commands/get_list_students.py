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
from track.management.tracked_command import TrackedCommand
from student.models import CourseEnrollment

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
		course_key = 'course-v1:ESPOL+HCDEA01+2017'
		if options['course']:
			course_key = options['course']

		try:
			course = CourseKey.from_string(course_key)
		# if it's not a new-style course key, parse it from an old-style
		# course key
		except InvalidKeyError:
			course = SlashSeparatedCourseKey.from_deprecated_string(course_key)

		nombre_acrchivo = 'listado_estudiantes.csv'
		fl = open(nombre_acrchivo, 'wb')
		writer = csv.writer(fl, delimiter=',')		

		lista_enrolados = CourseEnrollment.objects.filter(course_id=course)
		for enrolado in lista_enrolados:
			##enrolado.mode = 'honor'
			##enrolado.save()
			writer.writerow([
				enrolado.user.username,
				#enrolado.user.name,
				#enrolado.user.lastname,
				smart_str(enrolado.user.profile.name),
				enrolado.user.email,
				course_key
			])
		fl.close()