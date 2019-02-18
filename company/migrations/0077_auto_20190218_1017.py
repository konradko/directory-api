# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-18 10:17
from __future__ import unicode_literals

import directory_validators.company
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0076_auto_20190211_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='company_type',
            field=models.CharField(choices=[('COMPANIES_HOUSE', 'Company in Companies House'), ('SOLE_TRADER', 'Sole Trader')], default='COMPANIES_HOUSE', max_length=15),
        ),
        migrations.AlterField(
            model_name='company',
            name='number',
            field=models.CharField(blank=True, help_text='For companies registered in companies house this is their companies house number. For sole trader this is any randomly generated string.', max_length=8, null=True, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_company_number', message='Company number must be 8 characters', regex='^[A-Za-z0-9]{8}$'), directory_validators.company.no_html]),
        ),
    ]