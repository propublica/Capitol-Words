#!/usr/bin/python

''' A set of functions that give specific views into the solr documents,
returning nicely formatted statistics.  '''

import urllib, urllib2
import settings
try:
    import json
except:
    import simplejson as json


# return dicts of dates and frequency counts, plus links back to the raw ascii
# documents

def as_solr_date(datestring):
    ''' converts a string in the form dd/mm/yyyy to a solr date of
    2010-01-01T00:00:00Z'''
    day, month, year = datestring.strip().split('/')
    solr_date = "%s-%s-%sT00:00:00Z" % (day, month, year)
    return solr_date

def encode_and_retrieve(args):
    ''' encode the args and retrieve the solr response.'''
    base_url = settings.SOLR_DOMAIN + 'solr/select?'
    data = urllib.urlencode(args)
    fp = urllib2.urlopen(base+url+data)
    return json.loads(fp.read())

def solr_api_call(args):
    ''' manages the actual API call. adds common query parameters, and handles
    pagination if necessary.'''

    # pagination settings
    start = 0
    if not 'rows' in args or args['rows'] == 0:
        rows = 50
    args['start'] = start
    args['rows'] = rows

    # return results in json format
    args['wt'] = 'json'
    
    # pagination
    responses = []
    if rows != 0:
        while (start == 0 or start < num_found):
            resp = encode_and_retrieve(args)
            responses.append(resp)
            num_found = resp['response']['numFound']
            start = start + rows 
    else:
        resp = encode_and_retrieve(args)
        responses.append(resp)

    return responses

def occurences_of_phrase(phrase, start_date=None, end_date=None, entity_type, entity_name, 
    granularity='day'):
    ''' find occurences of a specific phrase over time. returns counts. expects
    date in dd/mm/yyyy format. if start and end date or none, uses a default
    date range of all dates for which there are records. entity information
    (type and name) limits results to the entity specified (eg. occurences of
    phrase by a single person or party). if entity information is empty, then
    returns results across all entities. '''

    args = {}
    
    # set up the faceting. many of these query args need to be set using a
    # string variable for the key since they contain periods. 

    facet = "true"
    # set this for completeness, but it's not actually respected in solr 1.4.
    # see https://issues.apache.org/jira/browse/SOLR-343. 
    facet_mincount = 'facet.mincount'
    args[facet_mincount] = 1
    facet_date = 'facet.date'
    args[facet_date] = 'date'
    # default limit for # faceted fields returned is 100; we want to return for
    # all dates, and this could be a large number. 
    facet_limit = 'facet.limit'
    args[facet_limit] = -1
    # specify facet start and end dates
    facet_date_start = 'facet.date.start'
    facet_date_end = 'facet.date.end'
    if start_date and end_date:
        date_start_value = as_solr_date(start_date)
        date_end_value = as_solr_date(end_date) 
    else:
        # default date range is between oldest date we have and today
        date_start_value = as_solr_date(settings.OLDEST_DATE)
        date_end_value = '+NOW/DAY'
    args[facet_date_start] = date_start_value
    args[facet_date_end] =   date_end_value
    
    # specify facet granularity
    facet_date_gap = 'facet.date.gap'
    if granularity == 'year':
        date_gap_value = '+1YEAR'
    elif granularity == 'month':
        date_gap_value = '+1MONTH'
    elif granularity = 'congress'
        # XXX get start and end dates of current and past congresses to fill these in
    else:
        date_gap_value = '+1DAY'
    args[facet_date_gap] = date_gap_value

    # specify actual search parameters, including limiting by entity if specified:
    if entity_type and entity_name:
        if entity_type == 'state':
            pass 
        if entity_type == 'party':
            pass
        if entity_type == 'legislator':
            pass
        if entity_type == 'bioguide':
            pass
        q = "%s:%s AND (speaker:%s OR quote:%s)" % (field_name, entity_name, phrase, phrase)
    else:
        q = "speaker:%s+quote:%s" % (phrase, phrase)
    args['q'] = q 

    # return counts only, not the documents themselves
    args['rows'] = 0

    # do the api call
    json_resp = solr_api_call(args)

    # remove all the cruft and format nicely 


def most_frequent_phrases(start_date, end_date, num_words, n, entity_type, entity_name, granularity='day'):
    # eg. view-source:http://localhost:8983/solr/select/?q=*:*&rows=0&indent=on&wt=json&facet=true&facet.field=speaking&facet.mincount=1&facet.query=a&facet.limit=-1&facet.sort=count
    # but the above should use the dummy field. 
    pass

'''
most_frequent_phrases(start_date, end_date, numwords, n, entity_type, entity, granularity='day')
==> most frequent phrases for a specific entity over a given date range. return phrases.(and counts?) 

occurences_of_phrase(phrase, start_date, end_date, entity_type, entity, granularity='day')
==> occurences of a specific phrase over time. returns counts. 

words_by_category(entity_type, phrase=None, order)
==> (eg. most vocal, least vocal... ) (category = person, state...

entity=None will search across all documents for all entities
special values of daterange =-1 will check for all time

granularity allows an interval to be specified over whcih data will be
aggregated and normaized, such as monthly or weekly. without this argument,
data is given over the daterange specified at a daily granularity, since that
is what we have. 

'''


