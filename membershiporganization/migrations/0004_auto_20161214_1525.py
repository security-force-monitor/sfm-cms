# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-12-14 15:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membershiporganization', '0003_auto_20161214_1456'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='membershiporganizationmember',
            table='membershiporganization_m',
        ),
    ]
