# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, Q
from elasticsearch_dsl.connections import connections
import logging

logger = logging.getLogger(__name__)

connections.create_connection(hosts=[settings.ES_URL], timeout=20)

QUERIES = {
    'title': 'get_title',
    'speaker': 'get_speaker'
}


def make_search():
    return Search(index=settings.ES_CW_INDEX)


def execute_search(query, sorting=None):
    search = make_search()
    if sorting:
        search = search.sort(sorting)
    results = search.query(query).execute()
    if results.success():
        return results
    return False


def index(request):
    return HttpResponse("Hello, world.")


def get_speaker(name):
    return Match(speakers=name)


def get_title(title):
    return Match(title=title)


def search_by_speaker(request, name):
    query = get_speaker(name)
    response = execute_search(query, '-date')
    if response.success():
        return JsonResponse(response.to_dict())


def search_by_title(request, title):
    query = get_title(title)
    response = execute_search(query, '-date')
    if response.success():
        return JsonResponse(response.to_dict())


def search_by_params(request):
    logger.debug("search_by_params")
    search = make_search().sort('-date')
    params = request.GET
    queries = []
    for f in QUERIES:
        if f in params:
            queries.append(globals()[QUERIES[f]](params[f]))
    logger.info("queries? %s " % queries)
    q = Q('bool', must=queries)
    response = search.query(q).execute()
    if response.success():
        return JsonResponse(response.to_dict())
    return JsonResponse("Found nothing")

