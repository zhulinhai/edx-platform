# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0011_auto_20161226_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificatehtmlviewconfiguration',
            name='configuration',
            field=models.TextField(default=b'{"default": {"accomplishment_class_append": "accomplishment-certificate", "platform_name": "LLPA Training Platform", "logo_src": "/static/images/logo.png", "logo_url": "", "company_verified_certificate_url": "https://edx.org/verified-certificate", "company_privacy_url": "/privacy", "company_tos_url": "/tos", "company_about_url": "/about"}, "verified": {"certificate_type": "Verified", "certificate_title": "Verified Certificate of Achievement"}, "honor": {"certificate_type": "Honor Code", "certificate_title": "Certificate of Achievement"}}', help_text=b'Certificate HTML View Parameters (JSON)'),
        ),
    ]

