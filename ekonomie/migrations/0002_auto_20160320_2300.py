# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-20 22:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ekonomie', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blackauction',
            name='seller_name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='entity',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='entity',
            name='units',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=256, unique=True),
        ),
    ]
