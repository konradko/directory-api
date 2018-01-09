# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-09 08:51
from __future__ import unicode_literals

import re

from django.core.management import call_command
from django.db import migrations, connection, transaction


def escape_ansi(line):
    """
    call_command output contains ANSI colour mark up, resulting in the shell
    showing the output in colour. That will interfere with code execution, so
    remote the ANSI colour mark up.
    
    """

    return re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', line)


def reset_supplier_primary_key_sequence(apps, schema_editor):
    # http://jesiah.net/post/23173834683/postgresql-primary-key-syncing-issues
    # the primary key sequence went out of sync because migraiton
    # 0002_auto_20180103_1159.py explicitly sets the id.

    sql = escape_ansi(call_command('sqlsequencereset', 'supplier'))
    cursor = connection.cursor()
    cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0002_auto_20180103_1159'),
    ]

    operations = [
        migrations.RunPython(
            reset_supplier_primary_key_sequence, migrations.RunPython.noop
        )
    ]
