# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-10 20:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('natica', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fitsfile',
            name='release_date',
            field=models.DateField(),
        ),
    ]