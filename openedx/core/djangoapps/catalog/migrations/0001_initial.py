# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogIntegration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('change_date', models.DateTimeField(auto_now_add=True, verbose_name='Change date')),
                ('enabled', models.BooleanField(default=False, verbose_name='Enabled')),
                ('internal_api_url', models.URLField(help_text='DEPRECATED: Use the setting COURSE_CATALOG_API_URL.', verbose_name='Internal API URL')),
                ('cache_ttl', models.PositiveIntegerField(default=0, help_text='Specified in seconds. Enable caching of API responses by setting this to a value greater than 0.', verbose_name='Cache Time To Live')),
                ('service_username', models.CharField(default=b'lms_catalog_service_user', help_text='Username created for Course Catalog Integration, e.g. lms_catalog_service_user.', max_length=100)),
                ('page_size', models.PositiveIntegerField(default=100, help_text='Maximum number of records in paginated response of a single request to catalog service.', verbose_name='Page Size')),
                ('changed_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='Changed by')),
            ],
            options={
                'ordering': ('-change_date',),
                'abstract': False,
            },
        ),
    ]
