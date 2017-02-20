# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-20 17:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hellocount', '0013_historicalrelic_relic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalplayer',
            name='rps',
            field=models.BigIntegerField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='rps',
            field=models.BigIntegerField(db_index=True, null=True),
        ),
    ]
