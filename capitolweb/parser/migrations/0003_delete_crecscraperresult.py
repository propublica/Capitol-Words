# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-08-22 12:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parser', '0002_crecparserresult'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CRECScraperResult',
        ),
    ]