# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-17 08:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20160416_0911'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='is_makable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='entity',
            name='is_markatable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='entity',
            name='is_minable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='entity',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]
