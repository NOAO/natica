# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-26 22:07
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('natica', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fitsfile',
            name='extras',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
    ]