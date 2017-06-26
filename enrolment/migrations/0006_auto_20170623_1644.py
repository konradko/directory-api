# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-06-23 16:44
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('enrolment', '0005_trustedsourcesignupcode_squashed_0006_auto_20170620_1029'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trustedsourcesignupcode',
            name='generated_by',
        ),
        migrations.DeleteModel(
            name='TrustedSourceSignupCode',
        ),
    ]
