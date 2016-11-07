# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-11-07 19:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0017_auto_20160826_2057'),
        ('area', '0004_auto_20160810_2017'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaOSMId',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('value', models.IntegerField(blank=True, default=None, null=True)),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='area.Area')),
                ('sources', models.ManyToManyField(related_name='area_areaosmid_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AreaOSMName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('value', models.TextField(blank=True, default=None, null=True)),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='area.Area')),
                ('sources', models.ManyToManyField(related_name='area_areaosmname_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='areageoname',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='areageoname',
            name='sources',
        ),
        migrations.RemoveField(
            model_name='areageonameid',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='areageonameid',
            name='sources',
        ),
        migrations.DeleteModel(
            name='AreaGeoName',
        ),
        migrations.DeleteModel(
            name='AreaGeonameId',
        ),
    ]
