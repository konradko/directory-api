# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-29 17:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0081_auto_20190327_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='company_type',
            field=models.CharField(choices=[('COMPANIES_HOUSE', 'Company in Companies House'), ('SOLE_TRADER', 'Company not in Companies House')], default='COMPANIES_HOUSE', max_length=15),
        ),
    ]