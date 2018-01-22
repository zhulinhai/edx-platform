# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import openedx.core.djangoapps.xmodule_django.models
import model_utils.fields
import django.db.models.deletion
import lms.djangoapps.grades.models
import coursewarehistoryextended.fields
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ComputeGradesSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('change_date', models.DateTimeField(auto_now_add=True, verbose_name='Change date')),
                ('enabled', models.BooleanField(default=False, verbose_name='Enabled')),
                ('batch_size', models.IntegerField(default=100)),
                ('course_ids', models.TextField(help_text=b'Whitespace-separated list of course keys for which to compute grades.')),
                ('changed_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='Changed by')),
            ],
        ),
        migrations.CreateModel(
            name='CoursePersistentGradesFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('change_date', models.DateTimeField(auto_now_add=True, verbose_name='Change date')),
                ('enabled', models.BooleanField(default=False, verbose_name='Enabled')),
                ('course_id', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
                ('changed_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='Changed by')),
            ],
        ),
        migrations.CreateModel(
            name='PersistentCourseGrade',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('id', coursewarehistoryextended.fields.UnsignedBigIntAutoField(serialize=False, primary_key=True)),
                ('user_id', models.IntegerField(db_index=True)),
                ('course_id', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255)),
                ('course_edited_timestamp', models.DateTimeField(null=True, verbose_name='Last content edit timestamp', blank=True)),
                ('course_version', models.CharField(max_length=255, verbose_name='Course content version identifier', blank=True)),
                ('grading_policy_hash', models.CharField(max_length=255, verbose_name='Hash of grading policy')),
                ('percent_grade', models.FloatField()),
                ('letter_grade', models.CharField(max_length=255, verbose_name='Letter grade for course')),
                ('passed_timestamp', models.DateTimeField(null=True, verbose_name='Date learner earned a passing grade', blank=True)),
            ],
            bases=(lms.djangoapps.grades.models.DeleteGradesMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PersistentGradesEnabledFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('change_date', models.DateTimeField(auto_now_add=True, verbose_name='Change date')),
                ('enabled', models.BooleanField(default=False, verbose_name='Enabled')),
                ('enabled_for_all_courses', models.BooleanField(default=False)),
                ('changed_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='Changed by')),
            ],
        ),
        migrations.CreateModel(
            name='PersistentSubsectionGrade',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('id', coursewarehistoryextended.fields.UnsignedBigIntAutoField(serialize=False, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('course_id', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255)),
                ('usage_key', openedx.core.djangoapps.xmodule_django.models.UsageKeyField(max_length=255)),
                ('subtree_edited_timestamp', models.DateTimeField(null=True, verbose_name='Last content edit timestamp', blank=True)),
                ('course_version', models.CharField(max_length=255, verbose_name='Guid of latest course version', blank=True)),
                ('earned_all', models.FloatField()),
                ('possible_all', models.FloatField()),
                ('earned_graded', models.FloatField()),
                ('possible_graded', models.FloatField()),
                ('first_attempted', models.DateTimeField(null=True, blank=True)),
            ],
            bases=(lms.djangoapps.grades.models.DeleteGradesMixin, models.Model),
        ),
        migrations.CreateModel(
            name='VisibleBlocks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('blocks_json', models.TextField()),
                ('hashed', models.CharField(unique=True, max_length=100)),
                ('course_id', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='persistentsubsectiongrade',
            name='visible_blocks',
            field=models.ForeignKey(to='grades.VisibleBlocks', db_column=b'visible_blocks_hash', to_field=b'hashed'),
        ),
        migrations.AlterUniqueTogether(
            name='persistentcoursegrade',
            unique_together=set([('course_id', 'user_id')]),
        ),
        migrations.AlterIndexTogether(
            name='persistentcoursegrade',
            index_together=set([('passed_timestamp', 'course_id'), ('modified', 'course_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='persistentsubsectiongrade',
            unique_together=set([('course_id', 'user_id', 'usage_key')]),
        ),
        migrations.AlterIndexTogether(
            name='persistentsubsectiongrade',
            index_together=set([('modified', 'course_id', 'usage_key'), ('first_attempted', 'course_id', 'user_id')]),
        ),
    ]
