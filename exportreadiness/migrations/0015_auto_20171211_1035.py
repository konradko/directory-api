# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-11 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exportreadiness', '0014_auto_20171207_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triageresult',
            name='is_in_companies_house',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='triageresult',
            name='regular_exporter',
            field=models.NullBooleanField(),
        ),
    ]