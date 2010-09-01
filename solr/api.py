#!/usr/bin/python

''' A set of functions that give specific views into the solr documents,
returning nicely formatted statistics.  '''

# return dicts of dates and frequency counts, plus links back to the raw ascii
# documents

def api_call_setup(args):
    base_url = settings.SOLR_DOMAIN + 'solr/select?'
    # pagination settings-- start at record 0 and return 10 "rows" (results)
    # per page. 
    args['start'] = 0
    args['rows'] = 10
    # return results in json format
    args['wt'] = 'json'
    data = urllib.urlencode(args)
    fp = urllib2.urlopen(base+url+data)
    return json.loads(fp.read())

def occurences_of_phrase(phrase, daterange, entity=None, granularity='day'):
    args = []
    



def most_vocal_by_person(date, n):
    ''' get the n most vocal lawmakers.''' 
    pass

def least_vocal_by_person(date, n):
    ''' get the n least vocal lawmakers.''' 
    pass


def phrase_by_person(phrase, name):
    pass

def phrase_by_state(phrase, state):
    pass

def phrase_by_party(phrase, party):
    pass

def phrase_by_date(phrase, date):
    pass

def most_frequent(numwords=1, daterange ):
    ''' most popular (frequent) phrases over a given daterange'''
    pass

def most_frequent_over_daterange(start, end):
    pass


'''
most_frequent_phrases(daterange, numwords, n, entity_type, entity, granularity='day')
==> most frequent phrases for a specific entity over a given date range
occurences_of_phrase(phrase, daterange, entity_type, entity, granularity='day')
==> occurences of a specific phrase over time
words_by_category(entity_type, phrase=None, order)

entity=None will search across all documents for all entities
special values of daterange =-1 will check for all time

granularity allows an interval to be specified over whcih data will be
aggregated and normaized, such as monthly or weekly. without this argument,
data is given over the daterange specified at a daily granularity, since that
is what we have. 

'''


