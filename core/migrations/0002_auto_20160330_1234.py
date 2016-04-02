# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-30 10:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='game',
            options={'permissions': (('play_game', 'Can play the game as a team'),)},
        ),
        migrations.AddField(
            model_name='balance',
            name='reservation_cnt',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='members',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='balance',
            name='amount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='balance',
            name='blocked',
            field=models.PositiveIntegerField(default=0),
        ),
    ]