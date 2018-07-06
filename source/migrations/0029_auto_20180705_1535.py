# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-07-05 15:35
from __future__ import unicode_literals

import uuid

from django.db import migrations

def get_uuid(apps, schema_editor):
    AccessPoint = apps.get_model('source', 'AccessPoint')
    for row in AccessPoint.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0028_auto_20180705_1528'),
    ]

    operations = [
        migrations.RunPython(get_uuid, reverse_code=migrations.RunPython.noop)
    ]
