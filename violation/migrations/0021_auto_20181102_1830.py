# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-02 18:30
from __future__ import unicode_literals
from collections import namedtuple
import os

from django.db import migrations, models, connection
import django.db.models.deletion
from django.conf import settings


def make_admin_levels(apps, schema):
    Violation = apps.get_model('violation', 'Violation')
    ViolationAdminLevel1 = apps.get_model('violation', 'ViolationAdminLevel1')
    ViolationAdminLevel2 = apps.get_model('violation', 'ViolationAdminLevel2')
    Location = apps.get_model('location', 'Location')

    violations = Violation.objects.exclude(violationlocation__isnull=True)

    def get_or_create_location(geo):
        location, created = Location.objects.get_or_create(id=geo.id)

        if created:
            location.name = geo.name
            location.geometry = geo.geometry

            country_code = geo.country_code.lower()
            location.division_id = 'ocd-division/country:{}'.format(country_code)

            if location.feature_type == 'point':
                location.feature_type = 'node'
            else:
                location.feature_type = 'relation'

            location.save()

        return location

    for violation in violations:

        hierarchy = '''
            SELECT parents.*
            FROM osm_data AS parents
            JOIN (
            SELECT
              UNNEST(hierarchy) AS h_id,
              localname,
              tags,
              admin_level,
              name,
              geometry
            FROM osm_data
            WHERE id = %s
            ) AS child
            ON parents.id = child.h_id::integer
            WHERE parents.admin_level = '4'
              OR parents.admin_level = '6'
        '''

        location = violation.violationlocation_set.first()

        if location.value:

            cursor = connection.cursor()
            cursor.execute(hierarchy, [location.value.id])

            columns = [c[0] for c in cursor.description]
            results_tuple = namedtuple('OSMFeature', columns)

            hierarchy = [results_tuple(*r) for r in cursor]

            violation_info = {}
            sources = location.sources.all()

            if hierarchy:
                for member in hierarchy:
                    if int(member.admin_level) == 6:
                        admin1 = get_or_create_location(member)
                        admin_obj, created = ViolationAdminLevel1.objects.get_or_create(value=admin1,
                                                                                        object_ref=violation)
                    if int(member.admin_level) == 4:
                        admin2 = get_or_create_location(member)
                        admin_obj, created = ViolationAdminLevel2.objects.get_or_create(value=admin2,
                                                                                        object_ref=violation)

                    violation.save()


def remake_views(apps, schema_editor):
    sql_folder_path = os.path.join(settings.BASE_DIR, 'sfm_pc/management/commands/sql')

    violation_view = os.path.join(sql_folder_path, 'violation_view.sql')
    violation_source_view = os.path.join(sql_folder_path, 'violation_sources_view.sql')
    violation_export_view = os.path.join(sql_folder_path, 'violation_all_export_view.sql')

    with open(violation_view) as vv, open(violation_source_view) as vsv, open(violation_export_view) as vev:
        with connection.cursor() as curs:
            curs.execute(vv.read())
            curs.execute(vsv.read())
            curs.execute(vev.read())


class Migration(migrations.Migration):

    dependencies = [
        ('violation', '0020_auto_20181102_1638'),
    ]

    operations = [
        migrations.RunPython(make_admin_levels),
        migrations.RunPython(remake_views),
    ]
