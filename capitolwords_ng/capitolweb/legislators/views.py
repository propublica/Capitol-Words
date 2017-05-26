# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers

from .models import CongressPerson

# Create your views here.


def find_by_name(request, name):
    people = CongressPerson.objects.prefetch_related('terms').filter(official_full__icontains=name)
    response = serializers.serialize("json", people)
    return HttpResponse(response, content_type='application/json')
