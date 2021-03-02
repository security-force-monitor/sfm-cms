# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-02 18:53
from __future__ import unicode_literals

from django.conf import settings
from django.core.management import call_command
from django.db import connection, migrations, models

import os


def make_materialized_views(*args):
    # Copied primarily from 0007_auto_20181018_1551 migration
    sql_folder_path = os.path.join(settings.BASE_DIR, 'sfm_pc/management/commands/sql')

    association_view = os.path.join(sql_folder_path, 'association_view.sql')
    association_source_view = os.path.join(sql_folder_path, 'association_sources_view.sql')

    with open(association_view) as em, open(association_source_view) as es:
        with connection.cursor() as curs:
            curs.execute(em.read())
            curs.execute(es.read())


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0007_auto_20181018_1551'),
        ('organization', '0017_auto_20181227_1414'),
        ('location', '0009_auto_20190131_2040'),
    ]

    operations = [
        # Drop materialized views depending on association_associationarea
        migrations.RunSQL('''
            DROP MATERIALIZED VIEW IF EXISTS sfm_pc_areadownload
        ''', reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL('''
            DROP MATERIALIZED VIEW IF EXISTS association
        ''', reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL('''
            DROP MATERIALIZED VIEW IF EXISTS association_sources
        ''', reverse_sql=migrations.RunSQL.noop),
        # Update the foreign key reference to the appropriate data type.
        # (Location.id is already a BIGINT)
        migrations.RunSQL('''
            ALTER TABLE association_associationarea
            ALTER COLUMN value_id
            SET DATA TYPE BIGINT
        '''),
        # Remake the materialized views we dropped
        migrations.RunPython(
            make_materialized_views,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
