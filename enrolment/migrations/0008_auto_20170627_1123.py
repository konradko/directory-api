# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-06-27 11:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enrolment', '0007_preverifiedenrolment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='preverifiedenrolment',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='preverifiedenrolment',
            unique_together=set([('company_number', 'email_address')]),
        ),
    ]