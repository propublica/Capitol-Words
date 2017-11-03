# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class SpeakerWordCounts(models.Model):
    def __str__(self):
        return ",".join([self.crec_id, self.bioguide_id])
    bioguide_id = models.CharField(max_length=7, primary_key=True)
    crec_id = models.CharField(max_length=64)
    date = models.DateField()
    named_entities = models.TextField()
    noun_chunks = models.TextField()
