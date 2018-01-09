# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-08 22:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('natica', '0003_auto_20180108_1546'),
    ]

    operations = [
        migrations.CreateModel(
            name='TacInstrumentAlias',
            fields=[
                ('tac', models.CharField(help_text='Name used by TAC Schedule', max_length=20, primary_key=True, serialize=False)),
                ('hdr', models.ForeignKey(help_text='Name used in FITS header', on_delete=django.db.models.deletion.CASCADE, to='natica.Instrument')),
            ],
        ),
    ]
