# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 16:17
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('natica', '0007_auto_20170722_1034'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hdu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hdu_idx', models.PositiveSmallIntegerField()),
                ('xtension', models.CharField(blank=True, max_length=40)),
                ('bitpix', models.IntegerField()),
                ('naxis', models.PositiveSmallIntegerField()),
                ('naxisN', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), default=list, size=None)),
                ('pcount', models.PositiveIntegerField(null=True)),
                ('gcount', models.PositiveIntegerField(null=True)),
                ('instrument', models.CharField(blank=True, help_text='INSTRUME', max_length=80)),
                ('telescope', models.CharField(blank=True, help_text='TELESCOP', max_length=80)),
                ('date_obs', models.DateTimeField(help_text='DATE-OBS', null=True)),
                ('obj', models.CharField(blank=True, help_text='OBJECT', max_length=80)),
                ('ra', models.CharField(max_length=20, null=True)),
                ('dec', models.CharField(max_length=20, null=True)),
                ('extras', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
        migrations.RemoveField(
            model_name='extensionhdu',
            name='fitsfile',
        ),
        migrations.RemoveField(
            model_name='primaryhdu',
            name='fitsfile',
        ),
        migrations.AddField(
            model_name='fitsfile',
            name='date_obs',
            field=models.DateTimeField(help_text='DATE-OBS', null=True),
        ),
        migrations.AddField(
            model_name='fitsfile',
            name='dec',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='fitsfile',
            name='instrument',
            field=models.CharField(default='foo', help_text='INSTRUME', max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fitsfile',
            name='ra',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='fitsfile',
            name='telescope',
            field=models.CharField(default='foo', help_text='TELESCOP', max_length=80),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='ExtensionHDU',
        ),
        migrations.DeleteModel(
            name='PrimaryHDU',
        ),
        migrations.AddField(
            model_name='hdu',
            name='fitsfile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='natica.FitsFile'),
        ),
    ]