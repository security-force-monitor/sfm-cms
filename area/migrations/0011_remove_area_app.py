# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-15 20:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('area', '0010_auto_20180706_1715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='areacode',
            name='accesspoints',
        ),
        migrations.RemoveField(
            model_name='areacode',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='areacode',
            name='sources',
        ),
        migrations.RemoveField(
            model_name='areacode',
            name='value',
        ),
        migrations.RemoveField(
            model_name='areadivisionid',
            name='accesspoints',
        ),
        migrations.RemoveField(
            model_name='areadivisionid',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='areadivisionid',
            name='sources',
        ),
        migrations.RemoveField(
            model_name='areageometry',
            name='accesspoints',
        ),
        migrations.RemoveField(
            model_name='areageometry',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='areageometry',
            name='sources',
        ),
        migrations.RemoveField(
            model_name='areaname',
            name='accesspoints',
        ),
        migrations.RemoveField(
            model_name='areaname',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='areaname',
            name='sources',
        ),
        migrations.RemoveField(
            model_name='areaosmid',
            name='accesspoints',
        ),
        migrations.RemoveField(
            model_name='areaosmid',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='areaosmid',
            name='sources',
        ),
        migrations.RemoveField(
            model_name='areaosmname',
            name='accesspoints',
        ),
        migrations.RemoveField(
            model_name='areaosmname',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='areaosmname',
            name='sources',
        ),
        migrations.DeleteModel(
            name='Area',
        ),
        migrations.DeleteModel(
            name='AreaCode',
        ),
        migrations.DeleteModel(
            name='AreaDivisionId',
        ),
        migrations.DeleteModel(
            name='AreaGeometry',
        ),
        migrations.DeleteModel(
            name='AreaName',
        ),
        migrations.DeleteModel(
            name='AreaOSMId',
        ),
        migrations.DeleteModel(
            name='AreaOSMName',
        ),
        migrations.DeleteModel(
            name='Code',
        ),
    ]