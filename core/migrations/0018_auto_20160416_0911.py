# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-16 07:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20160411_2158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='licences',
            field=models.ManyToManyField(blank=True, related_name='licenced_entities', to='core.Entity'),
        ),
    ]
