import re
from collections import defaultdict
import json
import urllib2
from optparse import make_option
import sys
import csv

from django.core.management.base import BaseCommand

from pymongo import Connection

import nltk
from dateutil.parser import parse as dateparse


connection = Connection()
db = connection['capitolwords']


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
            make_option('--date',
                         action='store',
                         dest='date',
                         default=None,
                         help='Date for which to generate n-grams'),
            )

    def list_dates(self):
        url = ('http://localhost:8983/solr/select'
               '?q=*:*'
               '&facet.mincount=1'
               '&rows=0'
               '&facet.field=date'
               '&wt=json'
               '&facet.method=enum'
               '&facet=true'
               '&facet.limit=1000000')

        data = json.loads(urllib2.urlopen(url).read())
        dates = [x.split('T')[0] for x in data['facet_counts']['facet_fields']['date'][::2]]
        return dates


    def make_ngrams(self, text, n):
        for graf in text:
            sentences = nltk.tokenize.sent_tokenize(graf.replace('\n', '').lower())
            for sentence in sentences:

                # Remove unnecessary punctuation
                sentence = re.sub(r"(\/|--\,|`|'|\(|\)\;\?)", ' ', sentence)
                sentence = re.sub(r"\.", '', sentence)

                #words = nltk.tokenize.word_tokenize(sentence)
                words = sentence.split()

                # Remove punctuation-only tokens
                words = [x for x in words
                            if re.search(r'[a-z]', x)]

                ngrams = nltk.util.ngrams(words, n)
                for ngram in ngrams:
                    yield ngram


    def save_ngram(self, doc, n, ngram, count):
        # Need to convert keys to strings for use as parameters
        s_doc = {}
        for k, v in doc.iteritems():
            s_doc[str(k)] = v
        doc = s_doc.copy()

        fieldnames = ['id', 'document_title', 'speaker_bioguide', 'speaker_state',
                      'speaker_firstname', 'speaker_lastname', 'speaker_party', 
                      'speaker_raw', 'date', 'pages', 'number', 'volume', 'chamber',
                      'granule', 'n', 'ngram', ]

        #doc['date'] = dateparse(doc['date']).date()
        doc['granule'] = re.search(r'(CREC-.*?)\.xml', doc['crdoc']).groups()[0]
        doc['n'] = n
        doc['ngram'] = ' '.join(ngram)
        doc['docid'] = doc['id']
        doc['count'] = count

        for key in ['speaking', 'quote', 'ingestdate', 'crdoc', 'id', 'title', 'rollcall', ]:
            try:
                del(doc[key])
            except KeyError:
                continue

        field = {1: 'unigrams',
                 2: 'bigrams',
                 3: 'trigrams',
                 4: 'quadgrams',
                 5: 'pentagrams', }[n]


        db[field].insert(doc)


    def handle(self, *args, **options):

        date = options['date']

        if date:
            dates = [date, ]

        else:
            dates = self.list_dates()

        for date in dates:
            url = ('http://localhost:8983/solr/select'
                   '?q=id:CREC-%s*'
                   '&facet.mincount=1'
                   '&rows=0'
                   '&facet.field=id'
                   '&wt=json'
                   '&facet=true'
                   '&facet.limit=1000000') % date

            data = json.loads(urllib2.urlopen(url).read())
            ids = data['facet_counts']['facet_fields']['id'][::2]

            for id in ids:
                print id

                url = 'http://localhost:8983/solr/select?q=id:%s&wt=json' % id
                doc = json.loads(urllib2.urlopen(url).read())['response']['docs'][0]

                speaking = doc.get('speaking', [])
                quote = doc.get('quote', [])
                doc['date'] = dateparse(doc['date'])

                for n in range(1,6):
                    ngrams = defaultdict(int)
                    for ngram in self.make_ngrams(text=speaking+quote, n=n):
                        ngrams[ngram] += 1

                    for ngram, count in ngrams.iteritems():
                        self.save_ngram(doc, n, ngram, count)

