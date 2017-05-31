# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect


def index(request):
    if settings.DEV_FRONTEND:
      return HttpResponseRedirect(settings.DEV_FRONTEND_SPA_BASE_URL)
    return HttpResponse("#resist")
