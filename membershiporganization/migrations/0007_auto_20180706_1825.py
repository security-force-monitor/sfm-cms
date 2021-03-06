# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-07-06 18:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0031_auto_20180705_1536'),
        ('membershiporganization', '0006_auto_20170907_1853'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershiporganizationfirstciteddate',
            name='accesspoints',
            field=models.ManyToManyField(related_name='membershiporganization_membershiporganizationfirstciteddate_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='membershiporganizationlastciteddate',
            name='accesspoints',
            field=models.ManyToManyField(related_name='membershiporganization_membershiporganizationlastciteddate_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='membershiporganizationmember',
            name='accesspoints',
            field=models.ManyToManyField(related_name='membershiporganization_membershiporganizationmember_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='membershiporganizationorganization',
            name='accesspoints',
            field=models.ManyToManyField(related_name='membershiporganization_membershiporganizationorganization_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='membershiporganizationrealend',
            name='accesspoints',
            field=models.ManyToManyField(related_name='membershiporganization_membershiporganizationrealend_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='membershiporganizationrealstart',
            name='accesspoints',
            field=models.ManyToManyField(related_name='membershiporganization_membershiporganizationrealstart_related', to='source.AccessPoint'),
        ),
    ]
