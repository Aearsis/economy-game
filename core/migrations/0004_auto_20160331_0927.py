# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-31 07:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20160330_2253'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='game',
            options={'permissions': (('play_game', 'Can play the game as a team'), ('control_game', 'Can control the game through control panel'))},
        ),
    ]
