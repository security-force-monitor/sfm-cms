# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-07-06 18:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0031_auto_20180705_1536'),
        ('geosite', '0012_auto_20170907_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='geositeadminid',
            name='accesspoints',
            field=models.ManyToManyField(related_name='geosite_geositeadminid_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='geositeadminlevel1',
            name='accesspoints',
            field=models.ManyToManyField(related_name='geosite_geositeadminlevel1_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='geositeadminlevel2',
            name='accesspoints',
            field=models.ManyToManyField(related_name='geosite_geositeadminlevel2_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='geositeadminname',
            name='accesspoints',
            field=models.ManyToManyField(related_name='geosite_geositeadminname_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='geositecoordinates',
            name='accesspoints',
            field=models.ManyToManyField(related_name='geosite_geositecoordinates_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='geositedivisionid',
            name='accesspoints',
            field=models.ManyToManyField(related_name='geosite_geositedivisionid_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='geositefirstcited',
            name='accesspoints',
            field=models.ManyToManyField(related_name='geosite_geositefirstcited_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='geositelastcited',
            name='accesspoints',
            field=models.ManyToManyField(related_name='geosite_geositelastcited_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='geositelocationid',
            name='accesspoints',
            field=models.ManyToManyField(related_name='geosite_geositelocationid_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='geositelocationname',
            name='accesspoints',
            field=models.ManyToManyField(related_name='geosite_geositelocationname_related', to='source.AccessPoint'),
        ),
        migrations.AddField(
            model_name='geositename',
            name='accesspoints',
            field=models.ManyToManyField(related_name='geosite_geositename_related', to='source.AccessPoint'),
        ),
    ]
