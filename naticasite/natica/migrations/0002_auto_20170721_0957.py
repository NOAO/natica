# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-21 16:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('natica', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fitsfile',
            name='archive_filename',
            field=models.CharField(default='foobar.fits', max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fitsfile',
            name='original_filename',
            field=models.CharField(default='snafu.fits', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='primaryhdu',
            name='fitsfile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='natica.FitsFile'),
        ),
    ]
