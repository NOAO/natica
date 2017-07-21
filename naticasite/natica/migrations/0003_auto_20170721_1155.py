# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-21 18:55
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('natica', '0002_auto_20170721_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extensionhdu',
            name='naxisN',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='extensionhdu',
            name='obj',
            field=models.CharField(blank=True, help_text='OBJECT', max_length=80),
        ),
        migrations.AlterField(
            model_name='primaryhdu',
            name='naxisN',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='primaryhdu',
            name='obj',
            field=models.CharField(blank=True, help_text='OBJECT', max_length=80),
        ),
    ]