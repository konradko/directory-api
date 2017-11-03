# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-03 11:57
from __future__ import unicode_literals

from django.db import migrations


def set_is_in_companies_house(apps, schema_editor):
    TriageResult = apps.get_model('exportreadiness', 'TriageResult')
    for triage_result in TriageResult.objects.all():
        triage_result.is_in_companies_house = not triage_result.sole_trader
        triage_result.save()


class Migration(migrations.Migration):

    dependencies = [
        ('exportreadiness', '0009_auto_20171103_1157'),
    ]

    operations = [
        migrations.RunPython(
        	set_is_in_companies_house, migrations.RunPython.noop
        ),
    ]
