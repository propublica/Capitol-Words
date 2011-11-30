from collections import defaultdict
from operator import itemgetter
from itertools import groupby
import re
import datetime
import json
import logging
import urllib
import urllib2

from django.conf import settings
from django.core.cache import cache
from django.db.models import *
from django.shortcuts import get_list_or_404, get_object_or_404
from django.db import connections, DatabaseError

from bioguide.models import *
from cwod_api.models import *
from ngrams.models import *

from piston.handler import BaseHandler
from piston.resource import Resource

from dateutil.parser import parse as dateparse
from dateutil.relativedelta import relativedelta
from pygooglechart import SimpleLineChart, PieChart2D, Axis
import numpy

from smooth import smooth

from cwod.utils import get_entry_detail_url

class GenericHandler(BaseHandler):

    DEFAULT_PER_PAGE = 50

    ENTITIES = {'state': 'speaker_state',
                'party': 'speaker_party',
                'bioguide_id': 'speaker_bioguide',
                'cr_pages': 'pages',
                'volume': 'volume',
                'congress': 'congress',
                'session': 'session',
                'id': 'id',
                'slug': 'slug',
                'page_id': 'page_id',
                }

    FIELDS = ['unigrams', 'bigrams', 'trigrams', 'quadgrams',
              'pentagrams', ]

    def as_solr_date(self, datestring):
        ''' converts a string in the form dd/mm/yyyy to a solr date of
        2010-01-01T00:00:00Z'''
        day, month, year = datestring.strip().split('/')
        solr_date = "%s-%s-%sT00:00:00Z" % (year, month, day)
        return solr_date

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

        offset = int(request.GET.get('page', 0)) * per_page
        return per_page, offset


    def read(self, request, *args, **kwargs):
        q = kwargs.get('q', [])

        per_page, offset = self.get_pagination(request)

        for k, v in self.ENTITIES.iteritems():

            param_val = None
            if k in request.GET and request.GET[k]: # Make sure value isn't blank
                param_val = request.GET[k]
            if k in kwargs and kwargs[k]:
                param_val = kwargs[k]

            # this is hacky, but the right way to do it seems to require changing ENTITIES, which
            # I'm loathe to do without fully understanding how it's used
            if k=='state' and param_val in ('OR', 'AND'): # not that it will ever be AND, but add reserved words as nec...
                param_val = '"%s"' % param_val

            if param_val is not None:
                q.append('%s:%s' % (v, param_val))


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
            q.append("date:[%s TO %s]" % (self.as_solr_date(start.strftime('%d/%m/%Y')),
                                          self.as_solr_date(end.strftime('%d/%m/%Y'))))

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
        #q.append('-document_title:"earmark declaration"')

        params = {'q': '(%s)' % ' AND '.join(q),
                  'facet': 'true',
                  'facet.field': facet_field,
                  'facet.limit': per_page,
                  'facet.offset': offset,
                  'facet.mincount': request.GET.get('mincount', 1),
                  'facet.sort': request.GET.get('sort', 'count'),
                  'facet.method': 'enumtermfreq',
                  'rows': '0',
                  'wt': 'json',
                  }

        if kwargs.get('sort'):
            params['sort'] = kwargs['sort']

        # Handle granularity.
        params.update(kwargs.get('params', {}))
        granularity = kwargs.get('granularity')
        if granularity and params['facet.field'] == 'date':
            if granularity == 'month':
                params['facet.field'] = 'year_month'
            elif granularity == 'year':
                params['facet.field'] = 'year'

        url = 'http://%s:%s/solr/select?%s' % (settings.SOLR_SERVER,
                                               settings.SOLR_PORT,
                                               urllib.urlencode(params))
        # print url
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
                            i['percentage'] = (i['count'] / float(total))*100
                        else:
                            i['percentage'] = 0
                    if show_totals or show_percentages or smoothing != 0:
                        i['total'] = total

            if smoothing != 0:
                smoothed = list(smooth([x['count'] for x in data], smoothing))
                for n, i in enumerate(data):
                    i['raw_count'] = i['count']
                    i['count'] = smoothed[n]
                    if show_percentages:
                        pct = (i['count'] / float(i['total']))*100
                        if pct == numpy.inf:
                            continue
                        else:
                            i['percentage'] = pct

            if granularity == 'day' and smoothing == 0:
                for row in data:
                    row['raw_count'] = row['count']

            # If the mincount is 0, remove any leading
            # and trailing items with counts of 0, but
            # leave any internal items with counts of 0.
            if params['facet.mincount'] == '0' and kwargs.get('trim', 'false') == 'true':
                start, stop = 0, 0
                for start, row in enumerate(data):
                    #if row['raw_count'] > 0:
                    if row.get('raw_count', row.get('count')) > 0:
                        break
                for stop, row in enumerate(reversed(data)):
                    #if row['raw_count'] > 0:
                    if row.get('raw_count', row.get('count')) > 0:
                        break
                data = data[start:len(data)-stop]

            return {'results': data, }

        else:
            data = json.loads(results)

        return self.format_for_return(data, *args, **kwargs)


class PopularPhraseHandler(BaseHandler):
    """Most frequent phrases.
    """
    fields = ('ngram', 'count', 'tfidf', )
    DEFAULT_PER_PAGE = 50

    def read(self, request, *args, **kwargs):
        allowed_entities = {
                'legislator': {
                    'model': NgramsByBioguide,
                    'field': 'bioguide_id',
                    },
                'state': {
                    'model': NgramsByState,
                    'field': 'state',
                    },
                'date': {
                    'model': NgramsByDate,
                    'field': 'date',
                    },
                'month': {
                    'model': NgramsByMonth,
                    'field': 'month',
                    },
                }

        n = request.GET.get('n', 1)
        try:
            n = int(n)
        except ValueError:
            return {'error': 'Invalid phrase length.', 'results': []}

        if n > 5:
            return {'error': 'Invaid phrase length.', 'results': []}

        entity = request.GET.get('entity_type', '')
        if entity not in allowed_entities.keys():
            return {'error': 'Invalid entity.', 'results': []}

        entity = allowed_entities[entity]
        val = request.GET.get('entity_value', '')
        if not val:
            return {'error': 'Invalud entity value.', 'results': []}

        per_page, offset = self.get_pagination(request)

        model = entity['model']
        field = entity['field']

        if field == 'date':
            try:
                dateparse(val)
            except ValueError:
                return {'error': 'Invalid date.', 'results': []}

        query = {field: val, 'n': n}
        return model.objects.filter(**query)[offset:offset+per_page]


    def get_pagination(self, request):
        try:
            per_page = int(request.GET.get('per_page', self.DEFAULT_PER_PAGE))
        except ValueError:
            per_page = self.DEFAULT_PER_PAGE
        if per_page > self.DEFAULT_PER_PAGE:
            per_page = self.DEFAULT_PER_PAGE

        offset = int(request.GET.get('page', 0)) * per_page
        return per_page, offset


class PhraseByCategoryHandler(GenericHandler):

    def read(self, request, *args, **kwargs):
        if not 'phrase' in request.GET and not 'phrase' in kwargs:
            return {'error': 'A value for the "phrase" parameter is required.', 'results': []}

        phrase = request.GET.get('phrase') or kwargs.get('phrase')
        phrase = ' '.join(tokenize(phrase))
        n = len(phrase.split())
        try:
            field = self.FIELDS[n-1]
        except IndexError:
            return {'error': 'The value given for the "phrase" parameter is too long. A phrase of five words or fewer is required.', 'results': []}

        kwargs['q'] = ['%s:"%s"' % (field, phrase.strip('"').lower()), ]

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

def tokenize(term):
    from nltk import regexp_tokenize

    # Adapted From Natural Language Processing with Python
    regex = r'''(?xi)
    (?:H|S)\.\ ?(?:(?:J|R)\.\ )?(?:Con\.\ )?(?:Res\.\ )?\d+ # Bills
  | ([A-Z]\.)+                                              # Abbreviations (U.S.A., etc.)
  | ([A-Z]+\&[A-Z]+)                                        # Internal ampersands (AT&T, etc.)
  | (Mr\.|Dr\.|Mrs\.|Ms\.)                                  # Mr., Mrs., etc.
  | \d*\.\d+                                                # Numbers with decimal points.
  | \d\d?:\d\d                                              # Times.
  | \$?[,\.0-9]+                                            # Numbers with thousands separators, (incl currency).
  | (((a|A)|(p|P))\.(m|M)\.)                                # a.m., p.m., A.M., P.M.
  | \w+((-|')\w+)*                                          # Words with optional internal hyphens.
  | \$?\d+(\.\d+)?%?                                        # Currency and percentages.
  | \.\.\.                                                  # Ellipsis
  | [][.,;"'?():-_`]
    '''
    # Strip punctuation from this one; solr doesn't know about any of it
    tokens = regexp_tokenize(term,regex)
    # tokens = [re.sub(r'[.,?!]', '', token) for token in tokens]
    return tokens


class PhraseOverTimeHandler(GenericHandler):

    def read(self, request, *args, **kwargs):
        phrase = request.GET.get('phrase') or kwargs.get('phrase')
        if not phrase:
            return {'error': 'A value for the "phrase" parameter is required.', 'results': []}
        tokens = tokenize(phrase)
        phrase = ' '.join(tokens)
        if not phrase:
            return {'error': 'A value for the "phrase" parameter is required.', 'results': []}
        n = len(tokens)
        if n not in range(1, 6):
            return {'error': 'The value given for the parameter "n" is invalid. An integer between one and five is required.', 'results': [], }

        field = self.FIELDS[n-1]

        if request.GET.get('stem') == 'true':
            from nltk.stem import PorterStemmer
            stemmer = PorterStemmer()
            stemmed = stemmer.stem(phrase.lower())
            # print stemmed
            kwargs['q'] = ['stemmed_%s:"%s"' % (field, stemmed), ]

        else:
            kwargs['q'] = ['%s:"%s"' % (field, phrase.lower()), ]

        granularity = {'year': 'year',
                       'month': 'month',
                       'week': 'week',
                       'congress': '',
                       'day': 'day',
                        }.get(request.GET.get('granularity', 'day'), 'day')

        params = {'facet.field': 'date',
                  'facet.limit': request.GET.get('per_page', '-1'),
                  'facet.sort': request.GET.get('sort', 'index'),
                  'facet.mincount': request.GET.get('mincount', 1),
                  }
        kwargs['params'] = params
        kwargs['granularity'] = granularity
        kwargs['n'] = n
        kwargs['trim'] = request.GET.get('trim', 'false')

        kwargs['results_keys'] = [granularity, 'count', ]
        return super(PhraseOverTimeHandler, self).read(request, *args, **kwargs)


class ChartHandler(GenericHandler):

    def read(self, request, *args, **kwargs):
        self.request = request
        if kwargs.get('chart_type') == 'timeline':
            handler = PhraseOverTimeHandler()
            if request.GET.get('split_by_party') == 'true':
                resultsets = {}
                for party in ['R', 'D', ]:
                    kwargs['party'] = party
                    resultsets[party] = handler.read(request, *args, **kwargs)
                return {'results': {'url': self._partyline(resultsets), }, }

            elif request.GET.get('compare') == 'true':
                phrases = request.GET.get('phrases', '').split(',')[:5] # Max of 5 phrases
                parties = request.GET.get('parties', '').split(',')
                states = request.GET.get('states', '').split(',')
                #chambers = request.GET.get('chambers', '').split(',')

                colors = ['8E2844', 'A85B08', 'AF9703', ]

                metadata = []
                legend_items = []
                months = None

                key = 'count'
                if self.request.GET.get('percentages') == 'true':
                    key = 'percentage'

                granularity = self.request.GET.get('granularity')

                width = int(request.GET.get('width', 575))
                height = int(request.GET.get('height', 300))
                chart = SimpleLineChart(width, height)
                chart.set_grid(0, 50, 2, 5) # Set gridlines
                chart.fill_solid('bg', '00000000') # Make the background transparent
                chart.set_colours(colors)
                maxcount = 0

                # Use phrases as a baseline; that is, assume that
                # there's a corresponding value for the other filters.
                # If a filter doesn't have as many values as the number
                # of phrases, the corresponding phrase will not be
                # filtered.
                # (However, if a value is set for 'party' or 'state'
                # in the querystring, that will override any values
                # set in 'phrases' or 'parties.')
                for n, phrase in enumerate(phrases):
                    chart.set_line_style(n, thickness=2) # Set line thickness

                    if not phrase.strip():
                        continue
                    kwargs['phrase'] = phrase
                    legend = phrase
                    try:
                        kwargs['party'] = parties[n]
                    except IndexError:
                        pass

                    try:
                        kwargs['state'] = states[n]
                    except IndexError:
                        pass

                    if kwargs.get('party') and kwargs.get('state'):
                        legend += ' (%(party)s, %(state)s)' % kwargs
                    elif kwargs.get('party'):
                        legend += ' (%(party)s)' % kwargs
                    elif kwargs.get('state'):
                        legend += ' (%(state)s)' % kwargs

                    legend_items.append(legend)

                    data = handler.read(request, *args, **kwargs)
                    results = data['results']
                    counts = [x.get(key) for x in results]
                    if max(counts) > maxcount:
                        maxcount = max(counts)

                    chart.add_data(counts)
                    metadata.append(kwargs)

                # Duplicated code; should move into separate function.
                if self.request.GET.get('granularity') == 'month':
                    if not months:
                        months = [x['month'] for x in results]
                        januaries = [x for x in months if x.endswith('01')]
                        january_indexes = [months.index(x) for x in januaries]
                        january_percentages = [int((x/float(len(months)))*100) for x in january_indexes]
                        index = chart.set_axis_labels(Axis.BOTTOM, [x[:4] for x in januaries[::2]])
                        chart.set_axis_positions(index, [x for x in january_percentages[::2]])

                chart.y_range = (0, maxcount)

                if key == 'percentage':
                    label = '%.4f' % maxcount
                    label += '%'
                else:
                    label = int(maxcount)

                index = chart.set_axis_labels(Axis.LEFT, [label,])
                chart.set_axis_positions(index, [100,])

                # Always include a legend when comparing.
                chart.set_legend(legend_items)

                return {'results': {'metadata': metadata, 'url': chart.get_url()}}
                #return resultsets

            else:
                data = handler.read(request, *args, **kwargs)
                return {'results': {'url': self._line(data['results']), }, }

        elif kwargs.get('chart_type') == 'pie':
            handler = PhraseByCategoryHandler()
            kwargs['entity_type'] = request.GET.get('entity_type')
            data = handler.read(request, *args, **kwargs)
            if request.GET.get('output') == 'data':
                return {'data': self._pie(data['results'])}
            return {'results': {'url': self._pie(data['results']), }, }

        return {'error': 'Invalid chart type.', }

    def _pie(self, results):
        width = self.request.GET.get('width')
        height = self.request.GET.get('height')
        if width:
            width = int(width)
        else:
            width = 300

        if height:
            height = int(height)
        else:
            height = 220

        chart = PieChart2D(width, height)
        data = defaultdict(int)
        if self.request.GET.get('entity_type') == 'party':
            to_include = ['R', 'D', ]
            for result in results:
                if result['party'] in to_include:
                    data[result['party']] = result['count']
                else:
                    data['Other'] += result['count']

        data = data.items()
        counts = [x[1] for x in data]
        labels = [x[0] for x in data]

        party_colors = {'R': 'bb3110',
                        'D': '295e72',
                        'Other': 'efefef'}
        colors = [party_colors.get(label) for label in labels]

        chart.add_data(counts)
        if self.request.GET.get('labels', 'true') != 'false':
            chart.set_pie_labels(labels)
        chart.set_colours(colors)
        chart.fill_solid('bg', '00000000') # Make the background transparent
        if self.request.GET.get('output') == 'data':
            return (labels, counts)
        return chart.get_url()

    def _line(self, results):
        key = 'count'
        if self.request.GET.get('percentages') == 'true':
            key = 'percentage'
        counts = [x.get(key) for x in results]
        maxcount = max(counts)

        granularity = self.request.GET.get('granularity')
        times = [x.get(granularity) for x in results]

        width = int(self.request.GET.get('width', 575))
        height = int(self.request.GET.get('height', 300))
        chart = SimpleLineChart(width, height, y_range=(0, max(counts)))
        chart.add_data(counts)
        chart.set_line_style(0, thickness=2) # Set line thickness
        chart.set_colours(['E0B300',])
        chart.fill_solid('bg', '00000000') # Make the background transparent
        chart.set_grid(0, 50, 2, 5) # Set gridlines

        if self.request.GET.get('granularity') == 'month':
            months = [x['month'] for x in results]
            januaries = [x for x in months if x.endswith('01')]
            january_indexes = [months.index(x) for x in januaries]
            january_percentages = [int((x/float(len(months)))*100) for x in january_indexes]
            index = chart.set_axis_labels(Axis.BOTTOM, [x[:4] for x in januaries[::2]])
            chart.set_axis_positions(index, [x for x in january_percentages[::2]])

        if key == 'percentage':
            label = '%.4f' % maxcount
            label += '%'
        else:
            label = int(maxcount)
        index = chart.set_axis_labels(Axis.LEFT, [label,])
        chart.set_axis_positions(index, [100,])

        if self.request.GET.get('legend', 'true') != 'false':
            chart.set_legend([self.request.GET.get('phrase'), ])

        return chart.get_url()

    def _partyline(self, party_results):
        if self.request.GET.get('percentages') == 'true':
            key = 'percentage'
        else:
            key = 'count'

        maxcount = 0
        allcounts = []
        granularity = self.request.GET.get('granularity')
        months = []

        for party, results in party_results.iteritems():
            counts = [x.get(key) for x in results['results']]
            allcounts.append(counts)
            if max(counts) > maxcount:
                maxcount = max(counts)

            if granularity == 'month':
                months = [x['month'] for x in results['results']]
                januaries = [x for x in months if x.endswith('01')]
                january_indexes = [months.index(x) for x in januaries]
                january_percentages = [int((x/float(len(months)))*100) for x in january_indexes]

            #times = [x.get(granularity) for x in results['results']]

        width = int(self.request.GET.get('width', 575))
        height = int(self.request.GET.get('height', 318))
        chart = SimpleLineChart(width, height, y_range=(0, max(counts)))

        chart.fill_solid('bg', '00000000') # Make the background transparent
        chart.set_grid(0, 50, 2, 5) # Set gridlines

        if granularity == 'month':
            index = chart.set_axis_labels(Axis.BOTTOM, [x[:4] for x in januaries[::2]])
            chart.set_axis_positions(index, [x for x in january_percentages[::2]])

        if key == 'percentage':
            label = '%.4f' % maxcount
        else:
            label = int(maxcount)
        index = chart.set_axis_labels(Axis.LEFT, [label,])
        chart.set_axis_positions(index, [100,])

        for n, counts in enumerate(allcounts):
            chart.add_data(counts)
            chart.set_line_style(n, thickness=2) # Set line thickness

        colors = {'R': 'bb3110', 'D': '295e72', }
        chart_colors = []
        chart_legend = []
        for k in party_results.keys():
            chart_colors.append(colors.get(k, '000000'))
            chart_legend.append(k)
            chart.legend_position = 'b'

        chart.set_colours(chart_colors)

        if self.request.GET.get('legend', 'true') != 'false':
            chart.set_legend(chart_legend)
        return chart.get_url()


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
        return NgramDateCount.objects.filter(**kw).extra(select={"month": 'EXTRACT(YEAR_MONTH FROM date)'}).values_list('month').annotate(Sum('count'))
    elif kwargs.get('granularity') == 'year':
        return NgramDateCount.objects.filter(**kw).extra(select={"year": 'EXTRACT(YEAR FROM date)'}).values_list('year').annotate(Sum('count'))

    return NgramDateCount.objects.filter(**kw).values_list('date', 'count')


class SimilarDocumentHandler(GenericHandler):

    def read(self, request, *args, **kwargs):
        doc_id = request.GET.get('id')
        #params = {'q': 'id:%s AND speaker_bioguide:[\'\' TO *]' % origin_id,
        params = {'q': 'id:%s' % doc_id,
                  'mlt': 'true',
                  'mlt.fl': 'speaking,document_title',
                  'mlt.mindf': 1,
                  'mlt.mintf': 1,
                  'fl': 'score,document_title,date,crdoc',
                  'mlt.match_included': 'false',
                  'wt': 'json',
                  'mlt.rows': 10,
                  }

        url = 'http://%s:%s/solr/mlt?%s' % (settings.SOLR_SERVER,
                                            settings.SOLR_PORT,
                                            urllib.urlencode(params))

        results = urllib2.urlopen(url).read()
        data = json.loads(results)

        docs = set()
        for doc in data['response']['docs']:
            docs.add((create_gpo_url(doc['crdoc']), doc['document_title'], doc['score'], doc['date']))

        fields = ['origin_url', 'document_title', 'score', 'date', ]
        docs = [dict(zip(fields, doc)) for doc in docs]
        docs.sort(key=itemgetter('score'), reverse=True)
        return {'results': docs}


class FullTextSearchHandler(GenericHandler):

    def read(self, request, *args, **kwargs):

        per_page, offset = self.get_pagination(request)

        sort = None

        if 'phrase' in request.GET:
            kwargs['q'] = ['speaking:"%s"' % request.GET['phrase'], ]
            sort = None
            if 'title' in request.GET:
                kwargs['q'].append('document_title:"%s"' % request.GET['title'])
        elif 'title' in request.GET:
            kwargs['q'] = ['document_title:"%s"' % request.GET['title'],]
        else:
            kwargs['q'] = ['*:*',]
            #sort = 'id asc'

        if request.GET.get('cr_pages') or request.GET.get('page_id'):
            per_page = '1000'

        kwargs['params'] = {'facet': 'false',
                            'rows': per_page,
                            'start': offset,
                            #'sort': 'id asc',
                            }
        if request.GET.get('sort'):
            kwargs['params']['sort'] = request.GET['sort']

        return super(FullTextSearchHandler, self).read(request, *args, **kwargs)

    def format_for_return(self, data, *args, **kwargs):
        num_found = data['response']['numFound']
        results = [{'bioguide_id': x.get('speaker_bioguide'),
                    'date': re.sub(r'T\d\d\:\d\d:\d\dZ$', '', x['date']),
                    'speaking': x.get('speaking'),
                    'title': x.get('document_title', ''),
                    'origin_url': create_gpo_url(x.get('crdoc', '')),
                    'capitolwords_url': settings.CAPWORDS_ROOT +
                                        get_entry_detail_url(create_gpo_url(x.get('crdoc', '')),
                                                             x.get('document_title', '')),
                    'speaker_first': x.get('speaker_firstname'),
                    'speaker_last': x.get('speaker_lastname'),
                    'speaker_party': x.get('speaker_party'),
                    'speaker_state': x.get('speaker_state'),
                    'speaker_raw': x.get('speaker_raw'),
                    'pages': x.get('pages'),
                    'congress': x.get('congress'),
                    'session': x.get('session'),
                    'bills': x.get('bill'),
                    'chamber': x.get('chamber'),
                    'volume': x.get('volume'),
                    'number': x.get('number'),
                    'order': int(x.get('id', 0).split('.chunk')[1])
                 }
                 for x in data['response']['docs'] ]
        return {'num_found': num_found, 'results': results, }


class LegislatorLookupHandler(BaseHandler):

    def read(self, request, *args, **kwargs):
        path = request.get_full_path()
        data = cache.get(path)
        if data:
            return data

        bioguide_id = request.GET.get('bioguide_id', None)
        if not bioguide_id:
            is_third_party = False
            legislators = []
            allowed_params = ['chamber', 'party', 'congress', 'state', ]
            for k, v in request.GET.iteritems():
                if k in allowed_params and v:
                    kwargs[k] = v
                if k == 'party' and v == '3':
                    is_third_party = True
                    del kwargs[k]
            legislator_qs = LegislatorRole.objects.filter(**kwargs)
            if is_third_party:
                legislator_qs = legislator_qs.exclude(party__iexact='d').exclude(party__iexact='r')
            legislator_qs = legislator_qs.order_by('last')
            for legislator in legislator_qs:
                legislators.append({'name': unicode(legislator),
                                    'state': legislator.state,
                                    'party': legislator.party,
                                    'chamber': legislator.chamber,
                                    'district': legislator.district,
                                    'bioguide_id': legislator.bioguide_id,
                                    'slug': legislator.slug(),
                                    'congress': legislator.congress, })
            r = {'results': legislators}
            cache.set(path, r)
            return r

        legislators = LegislatorRole.objects.filter(bioguide_id=bioguide_id).order_by('-end_date')
        if not legislators:
            return {}
        legislator = legislators[0]

        results = {
                'bioguide_id': bioguide_id,
                'first': legislator.first,
                'middle': legislator.middle,
                'last': legislator.last,
                'state': legislator.state,
                'district': legislator.district,
                'full_name': legislator.name(),
                'slug': legislator.slug(),
                'honorific': legislator.honorific(),
                'party': legislator.party,
                }
        r = {'results': results}
        cache.set(path, r)
        return r


class BillDetailHandler(BaseHandler):

    fields = ('slug', 'bill', 'congress', 'bill_title', 'last_action', 'last_action_date',
              'summary', 'url', 'source',
                ('sponsor',
                    ('first', 'middle', 'last', 'position', 'party', 'state', ),
                ),
                ('cosponsors',
                    ('first', 'middle', 'last', 'position', 'party', 'state', ),
                ),
                ('crdoc_set',
                    ('slug', 'page_id', 'document_title', 'date', 'chamber', 'session',
                        ('legislators',
                            ('first', 'middle', 'last', 'position', 'party', 'state', ),
                        ),
                    ),
                ),
            )

    def read(self, request, *args, **kwargs):
        congress = request.GET.get('congress')
        slug = request.GET.get('slug')
        if not congress or not slug:
            return {'error': 'Congress and slug required', }

        try:
            bill = Bill.objects.get(congress=congress, slug=slug)
        except Bill.DoesNotExist:
            return {'error': 'Bill not found', }

        return bill


class BillListHandler(BaseHandler):

    fields = ('slug', 'bill', 'bill_title', 'source',
              ('crdoc_set',
                  ('page_id', ),
              ),
             )

    def read(self, request, *args, **kwargs):
        congress = request.GET.get('congress')
        if not congress:
            return {'error': 'Congress is required', }

        bills = Bill.objects.filter(congress=congress)
        return bills


class DocListHandler(BaseHandler):

    fields = ('document_title', 'slug', 'chamber', 'page_id',
                ('legislators',
                    ('first', 'middle', 'last', 'position', 'party', 'state', ),
                ),
                ('bills',
                    ('bill', 'bill_title', ),
                ),
                ('representativesentence_set',
                    ('sentence', ),
                ),
            )
    exclude = ('id', re.compile('^private_'))

    #required_fields = ('year', 'month', 'day', 'congress', 'session', )

    def read(self, request, *args, **kwargs):
        year = request.GET.get('year')
        month = request.GET.get('month')
        day = request.GET.get('day')

        congress = request.GET.get('congress')
        session = request.GET.get('session')

        if year and month and day:
            return CRDoc.objects.filter(date__day=day,
                                        date__year=year,
                                        date__month=month,
                                        congress=congress,
                                        session=session
                                        ).order_by('page_id')

        elif year and month:
            return CRDoc.objects.filter(date__year=year,
                                        date__month=month,
                                        congress=congress,
                                        session=session
                                        ).order_by('date').values_list('date', flat=True).distinct()

        elif year:
            return CRDoc.objects.filter(date__year=year,
                                        congress=congress,
                                        session=session
                                        ).order_by('date').values_list('date__month', flat=True).distinct()

class DocDetailHandler(BaseHandler):
    fields = ('document_title', 'slug', 'chamber', 'page_id', 'date', 'congress', 'session',
                ('legislators',
                    ('first', 'middle', 'last', 'position', 'party', 'state', 'bioguide_id', ),
                ),
                ('bills',
                    ('bill', 'bill_title', ),
                ),
                ('representativesentence_set',
                    ('sentence', ),
                ),
                ('similar_documents',
                    ('document_title', 'slug', 'chamber', 'page_id', 'date', 'congress', 'session',
                        ('legislators',
                            ('first', 'middle', 'last', 'position', 'party', 'state', 'bioguide_id', ),
                        ),
                    ),
                ),
            )
    exclude = ('id', re.compile('^private_'))

    def read(self, request, *args, **kwargs):
        congress = request.GET.get('congress')
        session = request.GET.get('session')
        page_id = request.GET.get('page_id')

        return CRDoc.objects.get(congress=congress,
                                 session=session,
                                 page_id=page_id)


class SimilarEntityHandler(GenericHandler):

    def read(self, request, *args, **kwargs):
        entity_type = request.GET.get('entity_type')
        entity_value = request.GET.get('entity_value')
        if not entity_type or not entity_value:
            return {'error': 'Must specify entity_type and entity_value', 'results': []}

        valid_entity_types = ['bioguide',
                              'date',
                              'month',
                              'state',
                              'year', ]

        cursor = connections['ngrams'].cursor()
        cursor.execute("SELECT b, cosine_distance FROM distance_%s WHERE a = %%s AND cosine_distance != 1 ORDER BY cosine_distance DESC" % entity_type, [entity_value, ])
        return {'results': [dict(zip([entity_type, 'distance', ], x)) for x in cursor.fetchall()]}


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


class MonthListHandler(GenericHandler):
    def read(self, request, *args, **kwargs):
        raw_months = Date.objects.extra(select={"month": 'EXTRACT(YEAR_MONTH FROM date)'}).values_list('month', flat=True).distinct()
        return raw_months

class DatesInMonthHandler(GenericHandler):
    def read(self, request, *args, **kwargs):
        dates = Date.objects.filter(date__year=request.GET.get('year'), date__month=request.GET.get('month')).order_by('date')
        return dates
