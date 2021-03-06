import json
import urllib.request
import subprocess
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.utils import ProgrammingError
from django.conf import settings


class Command(BaseCommand):
    help = 'Import raw location data into Location objects'

    TABLE_NAME = 'canonical_locations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--location_file',
            dest='location_file',
            default='fixtures/locations.geojson',
            help='Relative path to location file for import'
        )

    def handle(self, *args, **options):
        self.location_file = os.path.join(
            os.getcwd(),
            options['location_file'],
        )

        n_raw = self.import_raw_locations()

        if n_raw == 0:
            return

        n_inserted_or_updated = self.create_location_objects()

        try:
            assert n_inserted_or_updated == n_raw
        except AssertionError:
            message = 'Number of raw locations ({0}) does not match number of created or updated Location objects ({1})'.format(n_raw, n_inserted_or_updated)
            raise CommandError(message)

    def import_raw_locations(self):
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE IF EXISTS {}'.format(self.TABLE_NAME))
            self.stdout.write('Dropped existing table "{}"'.format(self.TABLE_NAME))

        process = subprocess.Popen([
            'ogr2ogr',
            '-f',
            'PostgreSQL',
            'PG:dbname={NAME} user={USER} password={PASSWORD} host={HOST} port={PORT}'.format(**settings.DATABASES['default']),
            self.location_file,
            '-nln',
            self.TABLE_NAME,
        ], stdout=subprocess.PIPE)

        output, error = process.communicate()

        if output:
            self.stdout.write(self.style.SUCCESS(output.decode('utf-8')))

        if error:
            self.stdout.write(self.style.ERROR(error.decode('utf-8')))
            raise CommandError('Could not import raw location file')

        with connection.cursor() as cursor:
            for column in ('sfm', 'tags'):
                try:
                    cursor.execute('''
                        ALTER TABLE {table_name}
                        ALTER COLUMN {column_name}
                        TYPE json USING {column_name}::json
                    '''.format(table_name=self.TABLE_NAME,
                               column_name=column))

                except ProgrammingError:
                    # Handle instance where there are no locations in the
                    # provided file.
                    with open(self.location_file, 'r') as f:
                        location_geojson = json.load(f)

                    assert len(location_geojson['features']) == 0
                    self.stdout.write('No locations in given file')
                    n_inserted = 0

                    break

                else:
                    cursor.execute('SELECT COUNT(*) FROM {}'.format(self.TABLE_NAME))

                    row = cursor.fetchone()

                    n_inserted, = row

        self.stdout.write(
            self.style.SUCCESS(
                'Imported {} records from raw location file'.format(n_inserted)
            )
        )

        return n_inserted

    def create_location_objects(self):
        insert = '''
            INSERT INTO location_location (
              id,
              name,
              feature_type,
              division_id,
              tags,
              sfm,
              adminlevel,
              adminlevel1_id,
              adminlevel2_id,
              geometry
            )
            SELECT
              location.id,
              location.sfm->>'location:name' AS name,
              CASE
                WHEN location.tags->>'type' = 'boundary' THEN 'boundary'
                ELSE location.type
              END AS feature_type,
              'ocd-division/country:' || LOWER(
                COALESCE(country.tags->>'ISO3166-1', location.tags->>'is_in:country_code')
              ) AS division_id,
              location.tags,
              location.sfm,
              location.tags->>'admin_level' AS adminlevel,
              adminlevel1.id AS adminlevel1_id,
              adminlevel2.id AS adminlevel2_id,
              location.wkb_geometry AS geometry
            FROM {table_name} AS location
            LEFT JOIN {table_name} AS country
              ON location.sfm->>'location:admin_level_2' = country.sfm->>'location:humane_id:admin'
            LEFT JOIN {table_name} AS adminlevel1
              ON location.sfm->>'location:admin_level_6' = adminlevel1.sfm->>'location:humane_id:admin'
              AND COALESCE(location.sfm->>'location:admin_level', '') != '6'
            LEFT JOIN {table_name} AS adminlevel2
              ON location.sfm->>'location:admin_level_4' = adminlevel2.sfm->>'location:humane_id:admin'
              AND COALESCE(location.sfm->>'location:admin_level', '') != '4'
            ON CONFLICT (id) DO UPDATE
              SET
                name = EXCLUDED.name,
                feature_type = EXCLUDED.feature_type,
                division_id = EXCLUDED.division_id,
                tags = EXCLUDED.tags,
                sfm = EXCLUDED.sfm,
                adminlevel = EXCLUDED.adminlevel,
                adminlevel1_id = EXCLUDED.adminlevel1_id,
                adminlevel2_id = EXCLUDED.adminlevel2_id,
                geometry = EXCLUDED.geometry
            RETURNING id
        '''.format(table_name=self.TABLE_NAME)

        with connection.cursor() as cursor:
            cursor.execute(insert)

            n_inserted_or_updated = len(cursor.fetchall())

        self.stdout.write(
            self.style.SUCCESS(
                'Inserted or updated {} location objects'.format(n_inserted_or_updated)
            )
        )

        return n_inserted_or_updated
