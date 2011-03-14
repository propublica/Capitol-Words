from itertools import groupby
import re
import datetime
import json
import urllib
import urllib2

from django.conf import settings
from django.db.models import *
from django.shortcuts import get_list_or_404, get_object_or_404

from bioguide.models import *
from cwod_api.models import NgramDateCount

from piston.handler import BaseHandler
from piston.resource import Resource

from dateutil.parser import parse as dateparse


class GenericHandler(BaseHandler):

    DEFAULT_PER_PAGE = 50

    ENTITIES = {'state': 'speaker_state',
                'party': 'speaker_party',
                #'legislator': 'speaker',
                'bioguide_id': 'speaker_bioguide',
                'cr_pages': 'pages',
                'volume': 'volume', 
                'congress': 'congress',
                'session': 'session',
                }

    FIELDS = ['unigrams', 'bigrams', 'trigrams', 'quadgrams',
              'pentagrams', ]

    def as_solr_date(self, datestring):
        ''' converts a string in the form dd/mm/yyyy to a solr date of
        2010-01-01T00:00:00Z'''
        day, month, year = datestring.strip().split('/')
        solr_date = "%s-%s-%sT00:00:00Z" % (year, month, day)
        return solr_date

    def smooth(self, data, smoothing):
        """Use a moving average to smooth a list of numbers.
        """
        for n, i in enumerate(data):
            if n-smoothing < 0:
                nums = data[:n+smoothing]
            else:
                nums = data[n-smoothing:n+smoothing]
            yield sum(nums)/float(len(nums))

    def format_for_return(self, data, *args, **kwargs):
        key = data['facet_counts']['facet_fields'].keys()[0]
        data = data['facet_counts']['facet_fields'][key]

        phrases = data[::2]
        counts = data[1::2]

        results_keys = kwargs.get('results_keys', ['phrase', 'count', ])
        results = [dict(zip(results_keys, x)) for x in zip(phrases, counts)]
        return {'results': results}

    def get_pagination(self, request):
        try:
            per_page = int(request.GET.get('per_page', self.DEFAULT_PER_PAGE))
        except ValueError:
            per_page = self.DEFAULT_PER_PAGE
        if per_page > self.DEFAULT_PER_PAGE:
            per_page = self.DEFAULT_PER_PAGE

        offset = int(request.GET.get('page', 0)) * self.DEFAULT_PER_PAGE
        return per_page, offset


    def read(self, request, *args, **kwargs):

        q = kwargs.get('q', [])

        per_page, offset = self.get_pagination(request)

        for k, v in self.ENTITIES.iteritems():
            if k in request.GET:
                if request.GET[k]: # Make sure value isn't blank
                    q.append('%s:%s' % (v, request.GET[k]))

        if 'date' in request.GET:
            date = dateparse(request.GET['date'])
            kwargs.update({'date': date})
            start = date.strftime('%d/%m/%Y')
            end = (date + datetime.timedelta(1)).strftime('%d/%m/%Y')
            q.append("date:[%s TO %s]" % (self.as_solr_date(start), self.as_solr_date(end)))

        elif 'start_date' in request.GET and 'end_date' in request.GET:
            start = dateparse(request.GET['start_date'])
            end = dateparse(request.GET['end_date'])
            kwargs.update({'start': start, 'end': end, })
            q.append("date:[%s TO %s]" % (self.as_solr_date(start.strftime('%d/%m/%y')),
                                          self.as_solr_date(end.strftime('%d/%m/%y'))))

        if 'chamber' in request.GET:
            valid_chambers = ['house',
                              'senate',
                              'extensions', ]
            selected_chambers = []
            for chamber in request.GET['chamber'].lower().split('|'):
                if chamber in valid_chambers:
                    selected_chambers.append(chamber)
            if selected_chambers:
                q.append('chamber:(%s)' % ' OR '.join([x.title() for x in selected_chambers]))

        if 'legislator' in request.GET:
            # Search the speaker_fullname field.
            pass

        # n can be set either as a request parameter or in kwargs
        n = kwargs.get('n', request.GET.get('n', 1))
        error = {'error': 'The value given for the parameter "n" is invalid. An integer between one and five is required.',
                 'results': [], }
        try:
            n = int(n)
        except ValueError:
            return error
        if n not in range(1, 6):
            return error

        facet_field = self.FIELDS[n-1]

        params = {'q': '(%s)' % ' AND '.join(q),
                  'facet': 'true',
                  'facet.field': facet_field,
                  'facet.limit': per_page,
                  'facet.offset': offset,
                  'facet.mincount': '1',
                  'facet.sort': request.GET.get('sort', 'count'),
                  'facet.method': 'enumtermfreq',
                  'rows': '0',
                  'wt': 'json',
                  }


        # Handle granularity.
        params.update(kwargs.get('params', {}))
        granularity = kwargs.get('granularity')
        if granularity and params['facet.field'] == 'date':
            if granularity == 'month':
                params['facet.field'] = 'year_month'
            elif granularity == 'year':
                params['facet.field'] = 'year'

        if request.GET.get('congress'):
            try:
                servers = [settings.SOLR_SERVERS[request.GET['congress']], ]
            except KeyError:
                return {'error': 'Invalid congress', 'results': []}
        else:
            servers = settings.SOLR_SERVERS.values()

        params['shards'] = []
        for server, port in servers:
            params['shards'].append('%s:%s/solr' % (server, port))
        params['shards'] = ','.join(params['shards'])

        url = 'http://%s:%s/solr/select?%s' % (server,
                                               port,
                                               urllib.urlencode(params))

        results = urllib2.urlopen(url).read()

        show_totals = request.GET.get('totals', 'false') == 'true'
        show_percentages = request.GET.get('percentages', 'false') == 'true'
        smoothing = 0

        # If faceting on the date field, remove the time, showing only the date.
        if params['facet.field'] in ('date', 'year_month', 'year'):
            results = results.replace('T12:00:00Z', '')
            data = json.loads(results)
            data = self.format_for_return(data, *args, **kwargs)['results']

            smoothing = int(request.GET.get('smoothing', 0))

            # If the client wants to show the total number
            # of ngrams on each date, get the numbers.
            if show_totals or show_percentages or smoothing != 0:
                date_counts = dict(counts_over_time(**kwargs))
                for i in data:
                    if granularity == 'day':
                        total = date_counts.get(dateparse(i[granularity]).date(), 0)
                    else:
                        total = date_counts.get(int(i[granularity]), 0)
                    if show_percentages:
                        if total:
                            i['percentage'] = i['count'] / float(total)
                        else:
                            i['percentage'] = 0
                    if show_totals or show_percentages or smoothing != 0:
                        i['total'] = total

            if smoothing != 0:
                smoothed = list(self.smooth([x['count'] for x in data], smoothing))
                for n, i in enumerate(data):
                    i['raw_count'] = i['count']
                    i['count'] = smoothed[n]
                    if show_percentages:
                        i['percentage'] = i['count'] / float(i['total'])

            if granularity == 'day' and smoothing == 0:
                for row in data:
                    row['raw_count'] = row['count']

            # If the mincount is 0, remove any leading
            # and trailing items with counts of 0, but
            # leave any internal items with counts of 0.
            if params['facet.mincount'] == '0' and kwargs.get('trim', 'false') == 'true':
                start, stop = 0, 0
                for start, row in enumerate(data):
                    if row['raw_count'] > 0:
                        break
                for stop, row in enumerate(reversed(data)):
                    if row['raw_count'] > 0:
                        break
                data = data[start:len(data)-stop]

            return {'results': data, }

        else:
            data = json.loads(results)

        return self.format_for_return(data, *args, **kwargs)


class PopularPhraseHandler(GenericHandler):
    """Most frequent phrases.
    """
    def read(self, request, *args, **kwargs):
        kwargs['q'] = ['id:CREC*', ]
        return super(PopularPhraseHandler, self).read(request, *args, **kwargs)


class PhraseByCategoryHandler(GenericHandler):

    def read(self, request, *args, **kwargs):
        if not 'phrase' in request.GET:
            return {'error': 'A value for the "phrase" parameter is required.', 'results': []}

        phrase = request.GET.get('phrase')
        n = len(phrase.split())
        try:
            field = self.FIELDS[n-1]
        except IndexError:
            return {'error': 'The value given for the "phrase" parameter is too long. A phrase of five words or fewer is required.', 'results': []}

        kwargs['q'] = ['%s:"%s"' % (field, phrase.strip('"')), ]

        facet_field = {'legislator': 'speaker_bioguide',
                       'state': 'speaker_state',
                       'party': 'speaker_party',
                       'bioguide_id': 'speaker_bioguide',
                       'volume': 'volume',
                       'chamber': 'chamber',
                       }.get(kwargs.get('entity_type'))

        if not facet_field:
            return {'error': 'Invalid entity type.', 'results': []}

        kwargs['results_keys'] = [kwargs['entity_type'], 'count', ]

        kwargs['params'] = {'facet.field': facet_field, }
        return super(PhraseByCategoryHandler, self).read(request, *args, **kwargs)


class PhraseTreeHandler(GenericHandler):

    def read(self, request, *args, **kwargs):
        kwargs['q'] = ['id:CREC*', ]

        phrase = request.GET['phrase'].lower()
        if phrase:
            phrase += ' '

        kwargs['params'] = {'facet.prefix': phrase, }

        pieces = request.GET['phrase'].split()
        n = len(pieces)+1
        if n > 5:
            n = '5'
        else:
            n = str(n)
        kwargs['n'] = n

        return super(PhraseTreeHandler, self).read(request, *args, **kwargs)


class PhraseOverTimeHandler(GenericHandler):

    def read(self, request, *args, **kwargs):
        phrase = request.GET.get('phrase')
        if not phrase:
            return {'error': 'A value for the "phrase" parameter is required.', 'results': []}
        n = len(phrase.split())
        if n not in range(1, 6):
            return {'error': 'The value given for the parameter "n" is invalid. An integer between one and five is required.', 'results': [], }

        field = self.FIELDS[n-1]
        kwargs['q'] = ['%s:"%s"' % (field, phrase), ]

        granularity = {'year': 'year',
                       'month': 'month',
                       'week': 'week',
                       'congress': '',
                       'day': 'day',
                        }.get(request.GET.get('granularity', 'day'), 'day')

        params = {'facet.field': 'date',
                  'facet.limit': '-1',
                  'facet.sort': 'index',
                  'facet.mincount': request.GET.get('mincount', 1),
                  }
        kwargs['params'] = params
        kwargs['granularity'] = granularity
        kwargs['n'] = n
        kwargs['trim'] = request.GET.get('trim', 'false')

        kwargs['results_keys'] = [granularity, 'count', ]
        return super(PhraseOverTimeHandler, self).read(request, *args, **kwargs)


def counts_over_time(*args, **kwargs):
    n = kwargs.get('n', 1)
    try:
        n = int(n)
    except ValueError:
        return {'error': 'The value given for the parameter "n" is invalid. An integer between one and five is required.', 'results': [], }

    kw = {'n': n, }
    if 'start_date' in kwargs:
        kw['date__gte'] = start_date
    if 'end_date' in kwargs:
        kw['date__lte'] = end_date
    
    if kwargs.get('granularity') == 'month':
        return NgramDateCount.objects.extra(select={"month": 'EXTRACT(YEAR_MONTH FROM date)'}).values_list('month').annotate(Sum('count'))
    elif kwargs.get('granularity') == 'year':
        return NgramDateCount.objects.extra(select={"year": 'EXTRACT(YEAR FROM date)'}).values_list('year').annotate(Sum('count'))

    return NgramDateCount.objects.filter(**kw).values_list('date', 'count')


class FullTextSearchHandler(GenericHandler):

    def read(self, request, *args, **kwargs):
        """
        if 'phrase' not in request.GET:
            # error
            pass
        """

        per_page, offset = self.get_pagination(request)

        if 'phrase' in request.GET:
            kwargs['q'] = ['text:"%s"' % request.GET['phrase'], ]
        else:
            kwargs['q'] = ['dummy:"dummyvalue"',]

        kwargs['params'] = {'facet': 'false',
                            'rows': per_page,
                            'start': offset,
                            }
        return super(FullTextSearchHandler, self).read(request, *args, **kwargs)

    def format_for_return(self, data, *args, **kwargs):
        num_found = data['response']['numFound']
        results = [{'bioguide_id': x.get('speaker_bioguide'),
                 'date': re.sub(r'T\d\d\:\d\d:\d\dZ$', '', x['date']),
                 'speaking': x.get('speaking'),
                 'title': x.get('document_title', ''),
                 'origin_url': create_gpo_url(x.get('crdoc', '')),
                 'speaker_first': x.get('speaker_firstname'),
                 'speaker_last': x.get('speaker_lastname'),
                 'speaker_party': x.get('speaker_party'),
                 'speaker_state': x.get('speaker_state'),
                 'speaker_raw': x.get('speaker_raw'),
                 'pages': x.get('pages'),
                 'congress': x.get('congress'),
                 'session': x.get('session'),
                 }
                 for x in data['response']['docs'] ]
        return {'num_found': num_found, 'results': results, }


class LegislatorLookupHandler(BaseHandler):

    def read(self, request, *args, **kwargs):
        bioguide_id = request.GET.get('bioguide_id', None)
        if not bioguide_id:
            return {}

        legislators = get_list_or_404(Legislator, bioguide_id=bioguide_id)
        legislator = legislators[0]

        results = {
                'bioguide_id': bioguide_id,
                'prefix': legislator.prefix,
                'first': legislator.first,
                'last': legislator.last,
                'suffix': legislator.suffix,
                'sessions': [],
                }
        for legislator in legislators:
            results['sessions'].append({'position': legislator.position,
                                        'party': legislator.party,
                                        'state': legislator.state,
                                        'congress': legislator.congress, })
        return results


def create_gpo_url(crdoc):
    """Convert the path used for the crdoc field to
    a URL that can be used to retrieve the full text
    of the document from the GPO.
    """
    m = re.search(r'(CREC-(\d{4}-\d{2}-\d{2}).*?)\.xml', crdoc)
    if not m:
        return ''

    id, date = m.groups()
    url = 'http://origin.www.gpo.gov/fdsys/pkg/CREC-%s/html/%s.htm' % (date, id)
    return url


