import json

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from capitolwords import capitolwords

capitolwords = capitolwords(api_key=settings.SUNLIGHT_API_KEY)


def congress_list(request):
    return


def congress_detail(request, congress):
    return


def congress_session_detail(request, congress, session):
    return


def congress_pagerange_detail(request, congress, session, pagerange):
    return


def legislator_list(request):
    return


def legislator_detail(request, bioguide_id):
    return


def state_list(request):
    return


def state_detail(request, state):
    return


def party_list(request):
    return


def party_detail(request, party):
    return


def wordtree(request):
    return

