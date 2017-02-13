#!/usr/bin/python

''' A set of functions that give specific views into the solr documents,
returning nicely formatted statistics.  '''

import datetime
import urllib, urllib2, sys, os

import site
ROOT = os.path.dirname(os.path.realpath(__file__))
site.addsitedir(os.path.join(ROOT, "../"))
import settings

try:
    import json
except:
    import simplejson as json

from dateutil.parser import parse as dateparse

from lib import volume_lookup


# return dicts of dates and frequency counts, plus links back to the raw ascii
# documents

def as_solr_date(datestring):
    ''' converts a string in the form dd/mm/yyyy to a solr date of
    2010-01-01T00:00:00Z'''
    day, month, year = datestring.strip().split('/')
    solr_date = "%s-%s-%sT00:00:00Z" % (year, month, day)
    return solr_date

def encode_and_retrieve(args):
    ''' encode the args and retrieve the solr response.'''
    base_url = os.path.join(settings.SOLR_DOMAIN, 'solr/select?')
    data = urllib.urlencode(args)
    full_url = base_url+data
    print full_url
    fp = urllib2.urlopen(full_url)
    return json.loads(fp.read())

def solr_api_call(args):
    ''' manages the actual API call. adds common query parameters, and handles
    pagination if necessary.'''

    # return results in json format
    args['wt'] = 'json'
    
    response = encode_and_retrieve(args)

    return [response, ]


def generic_query(*args, **kwargs):
    q = []
    args = {}

    if 'date' in kwargs:
        date = dateparse(kwargs['date'])
        start = date.strftime('%d/%m/%Y')
        end = (date + datetime.timedelta(1)).strftime('%d/%m/%Y')
        q.append("date:[%s TO %s]" % (as_solr_date(start), as_solr_date(end)))

    elif 'start_date' in kwargs and 'end_date' in kwargs:
        start = dateparse(kwargs['start_date']).strftime('%d/%m/%Y')
        end = dateparse(kwargs['end_date']).strftime('%d/%m/%Y')
        q.append("date:[%s TO %s]" % (as_solr_date(start), as_solr_date(end)))

    if 'phrase' in kwargs:
        q.append('text:%s' % kwargs['phrase'])

    if 'congress' in kwargs:
        volumes = volume_lookup(kwargs['congress'], kwargs.get('session'))
        if not volumes:
            volumes = ['0', ]
        q.append('volume:(%s)' % ' OR '.join(volumes))

    if 'chamber' in kwargs:
        valid_chambers = ['house',
                          'senate',
                          'extensions', ]
        selected_chambers = []
        for chamber in kwargs['chamber'].lower().split('|'):
            if chamber in valid_chambers:
                selected_chambers.append(chamber)
        if selected_chambers:
            q.append('chamber:(%s)' % ' OR '.join([x.title() for x in selected_chambers]))

    entities = {'state': 'speaker_state',
                'party': 'speaker_party',
                'legislator': 'speaker',
                'bioguide': 'speaker_bioguide', 
                'cr_pages': 'pages',
                'volume': 'volume',
                }

    for k, v in entities.iteritems():
        if k in kwargs:
            q.append('%s:%s' % (v, kwargs[k]))

    if len(q):
        args['q'] = '(%s)' % ' AND '.join(q)
    else:
        args['q'] = '*:*'

    return args


def phrase_over_time(*args, **kwargs):
    if 'phrase' in kwargs:
        kwargs['phrase'] = '"%(phrase)s"' % kwargs

    args = generic_query(*args, **kwargs)

    try:
        per_page = int(kwargs.get('per_page', 100))
    except ValueError:
        per_page = 100
    if per_page > 100:
        per_page = 100

    if 'start_date' in kwargs and 'end_date' in kwargs:
        start, end = re.findall(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', args.get('q', ''))
    else:
        start = as_solr_date(settings.OLDEST_DATE)
        end = 'NOW/DAY+1DAY'

    granularity = {'year': '+1YEARS',
                   'month': '+1MONTHS',
                   'week': '+7DAYS',
                   'congress': '',
                   'day': '+1DAY',
                    }.get(kwargs.get('granularity', 'day'), 'day')

    args.update({'facet': 'true',
                 'facet.limit': per_page,
                 'facet.method': 'enum',
                 'facet.mincount': 1,
                 'facet.date.gap': granularity,
                 'facet.sort': 'index',
                 'facet.offset': int(kwargs.get('page', 0)) * 100,
                 'facet.field': 'date',
                 'facet.date': 'date',
                 'facet.date.start': start,
                 'facet.date.end': end,
                 'rows': 0,
                 })

    json_resp = solr_api_call(args)
    return json_resp



def phrase_by_category(*args, **kwargs):
    if 'phrase' in kwargs:
        kwargs['phrase'] = '"%(phrase)s"' % kwargs

    args = generic_query(*args, **kwargs)

    try:
        per_page = int(kwargs.get('per_page', 100))
    except ValueError:
        per_page = 100
    if per_page > 100:
        per_page = 100

    facet_field = {'legislator': 'speaker_bioguide',
                   'state': 'speaker_state',
                   'party': 'speaker_party',
                   'bioguide': 'speaker_bioguide'}.get(kwargs.get('entity_type'))
    if not facet_field:
        raise NotImplementedError(kwargs.get('entity_type', ''))

    args.update({'facet': 'true',
                 'facet.limit': per_page,
                 'facet.method': 'enum',
                 'facet.mincount': 1,
                 'facet.sort': 'count',
                 'facet.offset': int(kwargs.get('page', 0)) * 100,
                 'facet.field': facet_field,
                 'rows': 0,
                 })

    json_resp = solr_api_call(args)
    return json_resp


def most_frequent_phrases(*args, **kwargs):
    args = generic_query(*args, **kwargs)

    try:
        per_page = int(kwargs.get('per_page', 100))
    except ValueError:
        per_page = 100
    if per_page > 100:
        per_page = 100

    facet_field = {'1': 'unigrams',
                   '2': 'bigrams',
                   '3': 'trigrams',
                   '4': 'quadgrams',
                   '5': 'pentagrams'}.get(kwargs.get('n', '1'), '1')

    args.update({'facet': 'true',
                 'facet.limit': per_page,
                 'facet.method': 'enum',
                 'facet.mincount': 1,
                 'facet.sort': 'count',
                 'facet.offset': int(kwargs.get('page', 0)) * 100,
                 'facet.field': facet_field,
                 'rows': 0,
                 })

    json_resp = solr_api_call(args)
    return json_resp


def full_text_search(*args, **kwargs):
    args = generic_query(*args, **kwargs)

    try:
        per_page = int(kwargs.get('per_page', 100))
    except ValueError:
        per_page = 100
    if per_page > 100:
        per_page = 100
    args.update({'rows': per_page,
                 'start': int(kwargs.get('page', 0)) * 100,
                })

    json_resp = solr_api_call(args)
    return json_resp
