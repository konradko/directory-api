# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-06-14 14:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enrolment', '0003_remove_enrolment_sqs_message_id'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Enrolment',
        ),
    ]