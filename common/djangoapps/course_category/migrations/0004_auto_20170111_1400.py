# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_category', '0003_auto_20161222_1259'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coursecategory',
            options={'verbose_name': 'Course Category', 'verbose_name_plural': 'Course Categories'},
        ),
    ]

