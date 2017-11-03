# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import SpeakerWordCounts


class SpeakerWordCountsAdmin(admin.ModelAdmin):

      list_display = ('crec_id', 'bioguide_id' ,'date')

admin.site.register(SpeakerWordCounts, SpeakerWordCountsAdmin)
