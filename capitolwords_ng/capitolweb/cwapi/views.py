# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import JsonResponse
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, Q, Range
from elasticsearch_dsl.connections import connections
from rest_framework.decorators import api_view
import datetime

import logging

logger = logging.getLogger(__name__)

connections.create_connection(hosts=[settings.ES_URL], timeout=20)

# This maps the query parameters to factory methods for the queries
QUERIES = {
    'title': 'get_title',
    'speaker': 'get_speaker',
    'content': 'get_content',
    'entity': 'get_entity'
}

TIME_PERIODS = {
    'day': 1,
    'week': 7,
    'month': 30,
}


def make_search():
    return Search(index=settings.ES_CW_INDEX)


def execute_search(query, sorting='-date_issued'):
    """
    Runs a search with basic handling for sorting
    :param query: the query to execute
    :param sorting: the type of sorting, i.e. -dateIssued
    :return: results or False
    """
    search = make_search().sort(sorting)
    results = search.query(query).execute()
    if results.success():
        return results
    return False


def get_speaker(name):
    return Match(speakers={"query": name, "operator": "and"})


def get_title(title):
    return Match(title={"query": title, "type": "phrase"})


def get_content(content):
    return Q('match', content={'query': content, 'operator': 'and'})


def get_entity(entity):
    return Match(named_entities={"query": entity, "operator": "and"})


def get_date_range(start, end="now/d"):
    return Range(date_issued={"gte": start, "lte": end})


@api_view(['GET'])
def search_by_speaker(request, name):
    """
    Search for a speaker by name
    :param request:
    :param name: name of the congress person speaking
    :return: list sorted by date_issued
    """
    query = get_speaker(name)
    response = execute_search(query)
    if response.success():
        return JsonResponse(response.to_dict())

@api_view(['GET'])
def search_by_title(request, title):
    """
    Search by title of a document
    :param request:
    :param title: the title
    :return: list of results sorted by date_issued
    """
    query = get_title(title)
    response = execute_search(query)
    if response.success():
        return JsonResponse(response.to_dict())


@api_view(['GET'])
def search_by_entities(request):
    """
    Search by title of a document
    entities are specified in the query param 'entity'
    :param request:
    :return: list of results sorted by date_issued
    """
    terms = request.GET.getlist('entity')
    queries = [get_entity(e) for e in terms]
    logger.info("queries? %s " % queries)
    q = Q('bool', must=queries)
    response = execute_search(q)
    if response.success():
        return JsonResponse(response.to_dict())

@api_view(['GET'])
def search_by_params(request):
    """
    Search by arbitrary params which can be combined and can also be lists

    title - search on the title field
    speaker - individual speakers
    content - search for text matches in the content add &highlight=<number> to include contextual
              matches of the given fragment size in the result (default is 200)
    entity - named entities
    start_date / end_date in form 2017-01-04, inclusive. end_date defaults to today.

    Example:
        http://localhost:8000/cwapi/search/multi/?title=Budget&entity=social%20security&entity=senate&speaker=sanders
        http://localhost:8000/cwapi/search/multi/?speaker=schumer&content=trump&highlight=1000
        http://localhost:8000/cwapi/search/multi/?title=Budget&speaker=sanders&start_date=2016-01-11&end_date=2017-01-04

    :param request:
    :return:
    """
    logger.debug("search_by_params")
    params = request.GET
    search = make_search().sort('-date_issued')
    queries = []
    for f in QUERIES:
        if f in params:
            for r in params.getlist(f):
                queries.append(globals()[QUERIES[f]](r))
    if 'start_date' in params:
        if 'end_date' in params:
            queries.append(get_date_range(params.get('start_date'), params.get('end_date')))
        else:
            queries.append(get_date_range(params.get('start_date')))
    logger.info("queries? %s " % queries)
    q = Q('bool', must=queries)

    if 'highlight' in params and 'content' in params:
        frag_size = params.get('highlight')
        if not frag_size.isnumeric():
            frag_size = 200
        response = search.highlight('content', fragment_size=frag_size).query(q).execute()
    else:
        response = search.query(q).execute()
    if response.success():
        return JsonResponse(response.to_dict())
    return JsonResponse("Found nothing")

@api_view(['GET'])
def count_of_term_in_content(request, term):
    """
    Count the mention of a term in content

    time_period(optional, default to 'month') - period of time to go
                                                back from today
                                                month | week | day

    Example:
        http://127.0.0.1:8000/cwapi/count/obamacare/?time_period=week
        http://127.0.0.1:8000/cwapi/count/obamacare/

    :param request:
    :param term: term whose occurances we are counting
    :return: number of occurances of the term in content
    """
    time_period = request.query_params.get('time_period', 'month')

    query = get_content(term)
    search = make_search()

    # Make this 0 or just remove when we have more recent data
    starting_delta = -365

    delta = TIME_PERIODS[time_period]
    today = datetime.datetime.today()
    start_date = today + datetime.timedelta(days=starting_delta - delta)
    end_date = today + datetime.timedelta(days=starting_delta)

    # gte: Greater or Equal, lte: Better than 4G? JK Less than or Equal
    date_filter = {'range':{'date_issued':{'gte': start_date, 'lte':end_date}}}
    count = search.query(query).filter(date_filter).count()

    previous_period_start_date = start_date + datetime.timedelta(days=-delta)
    previous_period_end_date = end_date + datetime.timedelta(days=-delta)
    previous_period_date_filter = {'range':{'date_issued':{'gte': previous_period_start_date, 'lte':previous_period_end_date}}}
    previous_period_count = search.query(query).filter(previous_period_date_filter).count()

    return JsonResponse(
        {
            'term': term,
            'count': count,
            'previous_period_count': previous_period_count,
            'time_period': time_period,
            'start_date': start_date,
            'end_date': end_date,
        }
    )
