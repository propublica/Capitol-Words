# -*- coding: utf-8 -*-
import logging
from collections import defaultdict
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.http import JsonResponse
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, Q, Range
from elasticsearch_dsl.connections import connections
from rest_framework.decorators import api_view
from django.core.paginator import Paginator

from legislators.models import CongressPerson
from cwapi.es_docs import CRECDoc, get_term_count_in_doc, get_term_count_agg, make_search


logger = logging.getLogger(__name__)


VALID_SEARCH_FIELDS = [
    'title', 'speaker', 'content'
]


def match_speaker_to_bioguide(speaker):
    """Look up a speaker in the legislators db by their full name, as it 
    appears in the CREC metadata.
    
    Args:
        speaker (str): The offical_full name of the speaker, as it should
            appear in the speakers section of a CREC doc.
    
    Returns:
        dict: A dict containing the speakers party, a link to their thumbnail
            image, and a link to their bio page on congress.gov.
    """
    # TODO: Get most recent entry? Or the one correct for that time?
    for person in CongressPerson.objects.filter(official_full=speaker):
        bio_page_url = 'https://www.congress.gov/member/{0}/{1}'.format(
            '-'.join(person.official_full.lower().split()), person.bioguide_id
        )
        return {
            'im_url': person.image_sm,
            'party': person.terms.last().party, 
            'bio_page_url': bio_page_url
        }
        

def get_date_range_from_args(request):
    """Expects a request object with either "start_date" and "end_date"
    or "days_ago" query arguments. Returns a tuple containing a start and an
    end datetime.
    
    Args:
        request (django.http.request.HttpRequest): A django request object.
    
    Returns:
        tuple: 2-item tuple containing a start and an end datetime.
    """
    if 'start_date' in request.GET and 'end_date' in request.GET:
        start_date_str = request.GET.get('start_date', '').strip()
        end_date_str = request.GET.get('end_date', '').strip()
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:
        days_ago = int(request.GET.get('days_ago', 30))
        end_date = datetime.utcnow()
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days_ago)
    return (start_date, end_date)


def get_text_search_results(start_date, end_date, terms, size=10, offset=0):
    """Runs a "match query against any provided field in the terms argument.
    Returns a list of docs as dicts including the search score.
    
    Args:
        start_date (datetime): Start of date range.
        end_date (datetime): End of date range.
        terms (dict): A dict mapping field name to search term, multiple fields
            are or'd together.
        size (int): The number of results to retrieve, defaults to 10.
        offset (int): The offset from the highest search result to return items
            from (for pagination).
    
    Returns:
        list: A list of CREC documents as dicts, reverse sorted by score.
    """
    search = CRECDoc.search()
    for field, search_term in terms.items():
        m = Match(**{field: {'query': search_term, 'type': 'phrase'}})
        search = search.query(m)
    search = search.filter(
        'range', date_issued={'gte': start_date, 'lte': end_date}
    )
    search = search.sort('_score')
    search = search[offset:offset+size]
    results = search.execute()
    data = []
    for r in results:
        d = r.to_dict()
        d['date_issued'] = r.date_issued.strftime('%Y-%m-%d')
        d['score'] = r.meta.score
        data.append(d)
    data.sort(key=lambda x: -x['score'])
    return data


@api_view(['GET'])
def search_text_match(request):
    """Runs a "match" query against any provided field.
    """
    start_date, end_date = get_date_range_from_args(request)
    offset = int(request.GET.get('offset', 0))
    size = int(request.GET.get('size', 10))
    terms = {}
    for field in VALID_SEARCH_FIELDS:
        value = request.GET.get(field)
        if value:
            terms[field] = value
    data = get_text_search_results(
        start_date, end_date, terms, size=size, offset=offset
    )
    return JsonResponse({
        'status': 'success',
        'data': data
    })


def get_term_counts_histogram(es_conn, term, start_date, end_date):
    """Runs an elasticsearchs scripted metric aggregation to count the
    ocurrences of the provided term in the content field of all CREC documents,
    bucketed by day.
    
    Args:
        es_conn :cls:`elasticsearch.Elasticsearch`: A connection to an
            elasticsearch cluster.
        term (str): Search term.
        start_date (datetime): Start of date range.
        end_date (datetime): End of date range.
    
    Returns:
        dict: A historam mapping a timestamp (format YYYY-MM-DD) to the count
            for that day.
    """
    results = get_term_count_in_doc(es_conn, term, start_date, end_date)
    aggs = get_term_count_agg(results)
    if aggs is None:
        raise Exception()
    histogram = {}
    dt = start_date
    while dt <= end_date:
        histogram[dt.strftime('%Y-%m-%d')] = 0
        dt += timedelta(days=1)
    for bucket in aggs:
        dt = datetime.strptime(bucket['key_as_string'], '%Y-%m-%dT%H:%M:%S.%fZ')
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        histogram[dt.strftime('%Y-%m-%d')] = bucket['term_counts']['value']
    return histogram


@api_view(['GET'])
def term_counts_by_day(request):
    es_conn = connections.get_connection()
    term = request.GET.get('term', '').strip().lower()
    start_date, end_date = get_date_range_from_args(request)
    histogram = get_term_counts_histogram(es_conn, term, start_date, end_date)
    return JsonResponse({
        'status': 'success',
        'data': {
            'daily_counts': histogram
        }
    })
    

@api_view(['GET'])
def search_results_page(request):
    es_conn = connections.get_connection()
    term = request.GET.get('q', '').strip().lower()
    days_ago = request.GET.get('days_ago', 30)
    size = request.GET.get('size', 10)
    offset = request.GET.get('offset', 0)
    start_date, end_date = get_date_range_from_args(request)
    prev_start_date = start_date - timedelta(days=int(days_ago))
    prev_end_date = end_date - timedelta(days=int(days_ago))
    current_histogram = get_term_counts_histogram(
        es_conn, term, start_date, end_date
    )
    prev_histogram = get_term_counts_histogram(
        es_conn, term, prev_start_date, prev_end_date
    )
    current_total = sum(current_histogram.values())
    prev_total = sum(prev_histogram.values())
    docs = get_text_search_results(
        start_date, end_date, {'content': term}, size=size, offset=offset
    )
    for doc in docs:
        doc['mentions'] = doc['content'].lower().count(term.lower())
        doc['search_phrase'] = term
        date_issued = datetime.strptime(doc['date_issued'], '%Y-%m-%d')
        doc['human_date'] = date_issued.strftime('%b %d, %Y')
        i = doc['content'].lower().find(term.lower())
        if i > 0:
            start = max(0, i - 100)
            end = min(len(doc['content']), i + 200)
            doc['snippet'] = doc['content'][start:end]
        speakers = doc.get('speakers', '').split(',')
        doc['speakers'] = []
        for s in speakers:
            matched_bioguide_data = match_speaker_to_bioguide(s)
            if matched_bioguide_data:
                doc['speakers'].append(matched_bioguide_data)
    return JsonResponse(
        {
            'delta': int(100 * ((current_total - prev_total) / float(max(prev_total, 1)))),
            'docs': docs,
            'term': term,
            'current_period': {
                'daily_breakdown': [
                    {'date': k, 'count': v} for k, v in current_histogram.items()
                ],
                'total_count': current_total
            },
            'previous_period': {
                'daily_breakdown': [
                    {'date': k, 'count': v} for k, v in prev_histogram.items()
                ],
                'total_count': prev_total
            },
            'start_date': start_date,
            'end_date': end_date,
        }
    )
