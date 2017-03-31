# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-28 16:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hellocount', '0015_auto_20170220_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalplayer',
            name='rps_last7',
            field=models.BigIntegerField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='rps_last7',
            field=models.BigIntegerField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalplayer',
            name='level',
            field=models.IntegerField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='level',
            field=models.IntegerField(db_index=True, null=True),
        ),
    ]
