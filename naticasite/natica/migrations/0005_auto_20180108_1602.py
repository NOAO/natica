# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-08 23:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('natica', '0004_tacinstrumentalias'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tacinstrumentalias',
            name='hdr',
        ),
        migrations.DeleteModel(
            name='TacInstrumentAlias',
        ),
    ]
