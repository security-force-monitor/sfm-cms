# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-08-24 18:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composition', '0009_auto_20180824_1840'),
    ]

    database_operations = [
        migrations.AlterField(
            model_name='compositionclassification',
            name='value',
            field=models.ForeignKey('Classification', db_constraint=False, db_index=True)
        )
    ]

    state_operations = [
        migrations.AlterField(
            model_name='compositionclassification',
            name='value',
            field=models.IntegerField(db_index=True, null=False)
        ),
        migrations.RenameField(
            model_name='compositionclassification',
            old_name='value',
            new_name='value_id'
        )
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
