# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-02 06:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hellocount', '0006_auto_20170202_0514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalplayer',
            name='guildname',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='guildname',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
