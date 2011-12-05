import datetime
from decimal import Decimal
from operator import itemgetter
from optparse import OptionParser
import csv
import json
import math
from optparse import make_option
import sys
import urllib
import urllib2

from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from ngrams.models import *


class Calculator(object):
    def __init__(self, facet_field, congress=None):
        #self.n = n
        #self.gram = ['unigrams', 'bigrams', 'trigrams', 'quadgrams', 'pentagrams', ][self.n-1]
        self.facet_field = facet_field
        self.url = 'http://ec2-184-72-184-231.compute-1.amazonaws.com:8983/solr/select'
        self.df = {}
        self.congress = congress

    def gram(self, n):
        return ['unigrams', 'bigrams', 'trigrams', 'quadgrams', 'pentagrams', ][n-1]

    def _query_solr(self, data):
        body = urllib.urlencode(data)
        url = '%s?%s' % (self.url, body)
        r = urllib2.urlopen(url)
        return json.loads(r.read())

    def docs(self):
        if not hasattr(self, 'numdocs'):
            if self.congress:
                q = 'congress:"%s"' % self.congress
            else:
                q = '*:*'
            kwargs = {'q': q,
                      'facet': 'true',
                      'rows': 0,
                      'facet.field': self.facet_field,
                      'facet.limit': -1,
                      'facet.mincount': 0,
                      'facet.method': 'enum',
                      'wt': 'json', }
            data = self._query_solr(kwargs)
            self.numdocs = Decimal(len(data['facet_counts']['facet_fields'][self.facet_field]) / 2)

        return self.numdocs

    def docfreq(self, n, ngram):
        q = ['%s:"%s"' % (self.gram(n), ngram), ]
        if self.congress:
            q.append('congress:"%s"' % self.congress)

        if not self.df.get(ngram):
            #kwargs = {'q': '%s:"%s"' % (self.gram(n), ngram),
            kwargs = {'q': ' AND '.join(q),
                      'facet': 'true',
                      'rows': 0,
                      'facet.field': self.facet_field,
                      'facet.limit': -1,
                      'facet.mincount': 1,
                      'facet.method': 'enum',
                      'wt': 'json', }
            data = self._query_solr(kwargs)
            self.df[ngram] = Decimal(len(data['facet_counts']['facet_fields'][self.facet_field]) / 2)
        return self.df.get(ngram)

    def list_facets(self):
        if self.congress:
            q = 'congress:"%s"' % self.congress
        else:
            q = '*:*'
        kwargs = {'q': q,
                  'facet': 'true',
                  'facet.field': self.facet_field,
                  'rows': 0,
                  'facet.method': 'enum',
                  'wt': 'json',
                  'facet.limit': -1,
                  'facet.mincount': 0, }
        data = self._query_solr(kwargs)
        return data['facet_counts']['facet_fields'][self.facet_field][::2]

    def list_ngrams_for_facet(self, n, facet):
        q = ['%s:"%s"' % (self.facet_field, facet), ]
        if self.congress:
            q.append('congress:"%s"' % self.congress)

        #kwargs = {'q': '(%s:"%s") AND speaker_bioguide:[\'\' TO *]' % (self.facet_field, facet),
        kwargs = {'q': ' AND '.join(q),
                  'facet': 'true',
                  'facet.field': self.gram(n),
                  'facet.method': 'enumtermfreq',
                  'facet.mincount': 3,
                  'wt': 'json',
                  'rows': 0,
                  'facet.limit': 1000, }
        data = self._query_solr(kwargs)
        data = data['facet_counts']['facet_fields'][self.gram(n)]
        return zip(data[::2], data[1::2])

    def get_date_diversity(self, bioguide, n, ngram):
        url = 'http://localhost:8983/solr/select'
        q = ['speaker_bioguide:"%s"' % bioguide,
             '%s:"%s"' % (self.gram(n), ngram),
             ]
        if self.congress:
            q.append('congress:"%s"' % self.congress)

        #kwargs = {'q': '(speaker_bioguide:"%s" AND %s:"%s")' % (bioguide, self.gram(n), ngram),
        kwargs = {'q': ' AND '.join(q),
                  'facet': 'true',
                  'facet.field': 'date',
                  'facet.method': 'enum',
                  'facet.mincount': 1,
                  'facet.limit': -1,
                  'wt': 'json', }
        data = self._query_solr(kwargs)
        data = data['facet_counts']['facet_fields']['date']
        return len(data)/2


def list_active_legislators_first():
    query = 'select bioguide_id from bioguide_legislatorrole group by bioguide_id order by max(end_date) desc, bioguide_id'
    from MySQLdb import Connection
    cursor = Connection('localhost', 'capwords', 'capwords', 'capwords').cursor()
    cursor.execute(query)
    results = [x[0] for x in cursor.fetchall()]
    return results

#if __name__ == '__main__':

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--field',
                action='store',
                dest='field',
                default=None,
                help='Field to calculate ngram tfidf for'),
            make_option('--congress',
                action='store',
                dest='congress',
                help='Restrict calculation to the given congress'),
            make_option('--values',
                action='store',
                dest='field_values',
                default=None,
                help='Specific values to iterate for field, if applicable'),
    )


    def handle(self, *args, **options):
        field = options.get('field')
        congress = options.get('congress')
        field_values = options.get('field_values')

        calculator = Calculator(field, congress)
        # generate facets based on somewhat sane defaults, or accept a comma-delimited list of strings to compare
        if field == 'speaker_bioguide':
            # already = set([(x[0], int(x[1])) for x in csv.reader(open(r'ngrams_by_bioguide.csv', 'r')) if len(x) > 1])
            already = set([(x.bioguide_id, int(x.n)) for x in NgramsByBioguide.objects.raw('select * from ngrams_ngramsbybioguide group by bioguide_id, n')])
            if field_values:
                facets = [args.strip() for arg in field_values.split(',')]
            facets = list_active_legislators_first()
        elif field == 'year_month':
            # already = set([(x[0], int(x[1])) for x in csv.reader(open(r'ngrams_by_month.csv', 'r')) if len(x) > 1])
            already = set([(x.month, int(x.n)) for x in NgramsByMonth.objects.raw('select * from ngrams_ngramsbymonth group by month, n')])
            if field_values:
                facets = [int(args.strip()) for arg in field_values.split(',')]
            else:
                facets = calculator.list_facets()
        elif field == 'date':
            already = []
            if field_values:
                dates = [args.strip() for arg in field_values.split(',')]
            else:
                dates = Date.objects.values_list('date', flat=True).order_by('-date').distinct()[:1]
            missing = []
            for date in dates:
                if NgramsByDate.objects.filter(date=date).count() == 0:
                    missing.append(date)
            facets = ['%sT12:00:00Z' % date.strftime('%Y-%m-%d') for date in missing]
        else:
            already = []
            facets = calculator.list_facets()

        for facet in reversed(facets):
            with transaction.commit_on_success():

                print facet
                for n in range(1,6):

                    if (facet, n) in already:
                        # recreate 'this' month, as calculated last week (we will run this weekly)
                        if field == 'year_month' and facet == (datetime.datetime.today() - datetime.timedelta(7)).strftime('%Y%m'):
                            pass
                        # always recreate terms for speakers
                        elif field == 'speaker_bioguide':
                            pass
                        else:
                            continue

                    ngrams = []
                    ngrams_for_facet = calculator.list_ngrams_for_facet(n, facet)
                    facet_total_ngrams = sum([x[1] for x in ngrams_for_facet])

                    for ngram, count in ngrams_for_facet:
                        try:
                            df = calculator.docfreq(n, ngram)
                            idf = math.log(calculator.docs() / df)
                            tf = count / float(facet_total_ngrams)
                            tfidf = tf * idf
                            if tfidf == 0:
                                continue
                            #diversity = calculator.get_date_diversity(facet, n, ngram)
                            ngrams.append((ngram, tfidf, count))
                        except:
                            #print 'ERROR'
                            continue

                    ngrams.sort(key=itemgetter(1), reverse=True)

                    for ngram, tfidf, count in ngrams:
                        output = map(str, [facet, n, ngram, tfidf, int(count), ])
                        if congress:
                            output.append(congress)
                        #writer.writerow(output)
                        if field == 'date':
                            NgramsByDate.objects.create(n=n,
                                                        date=date,
                                                        ngram=ngram,
                                                        tfidf=tfidf,
                                                        count=count)
                        if field == 'year_month':
                            NgramsByMonth.objects.filter(month=facet, n=n).delete()
                            NgramsByMonth.objects.create(n=n,
                                                         month=facet,
                                                         ngram=ngram,
                                                         tfidf=tfidf,
                                                         count=count)
                        if field == 'speaker_bioguide':
                            NgramsByMonth.objects.filter(bioguide_id=facet, n=n).delete()
                            NgramsByBioguide.objects.create(n=n,
                                                            bioguide_id=facet,
                                                            ngram=ngram,
                                                            tfidf=tfidf,
                                                            count=count)
