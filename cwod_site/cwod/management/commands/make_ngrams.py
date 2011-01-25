from collections import defaultdict
from httplib import HTTPConnection
from optparse import make_option
import csv
import json
import re
import sys
import urllib2

from django.core.management.base import BaseCommand

import pymongo
from pymongo import Connection

import nltk
from dateutil.parser import parse as dateparse
import lxml.etree


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
               '&facet.sort=index'
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
                sentence = re.sub(r"(\/|--|`|'|\(|\)\;\?)", ' ', sentence)
                sentence = re.sub(r"(\.|,)", '', sentence)

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


    def save_to_solr(self, doc):
        self.error = None
        con = HTTPConnection('localhost:8984')
        con.putrequest('POST', '/solr/update/')
        con.putheader('content-length', str(len(doc)))
        con.putheader('content-type', 'text/xml; charset=UTF-8')
        con.endheaders()
        con.send(doc)
        r = con.getresponse()
        if str(r.status) == '200':
            self.status = 'OK'
            #print r.read()
            self.commit()
        else:
            self.error = '%d: %s' % (r.status, r.read())
            print self.error

    def commit(self):
        DATA = '<commit/>'
        con = HTTPConnection('localhost:8984')
        con.putrequest('POST', '/solr/update/')
        con.putheader('content-length', str(len(DATA)))
        con.putheader('content-type', 'text/xml; charset=UTF-8')
        con.endheaders()
        con.send(DATA)
        r = con.getresponse()
        if not str(r.status) == '200':
            print 'error'
            #print r.read()
            #print r.status
        print 'Commit response: %s' % r.read()


    def handle(self, *args, **options):
        # Create indexes
        """
        for collection in ['unigrams', 'bigrams', 'trigrams', 'quadgrams', 'pentagrams', ]:
            db[collection].ensure_index([('ngram', pymongo.ASCENDING), ])
        """
        # Remove the entries from the last granule inserted,
        # to avoid duplicates.
        last_entry = db['unigrams'].find().sort('_id', -1)[0]
        for collection in ['unigrams', 'bigrams', 'trigrams', 'quadgrams', 'pentagrams', ]:
            db[collection].remove({'granule': last_entry['granule']})

        # Get a list of indexed granules so we don't
        # reindex them. 
        # TODO: Create a unique index to avoid duplicates.
        granules = db['unigrams'].distinct('granule')

        """
        if date:
            dates = [date, ]

        else:
            dates = self.list_dates()
        """
        dates = self.list_dates()

        for date in dates:
            url = ('http://localhost:8983/solr/select'
                   '?q=id:CREC-%s*'
                   '&facet.mincount=1'
                   '&rows=0'
                   '&facet.field=id'
                   '&wt=json'
                   '&facet=true'
                   '&facet.sort=index'
                   '&facet.limit=1000000') % date

            data = json.loads(urllib2.urlopen(url).read())
            ids = data['facet_counts']['facet_fields']['id'][::2]

            for id in ids:
                if id.split('.')[0] in granules:
                    continue

                print id

                url = 'http://localhost:8983/solr/select?q=id:%s&wt=json' % id
                doc = json.loads(urllib2.urlopen(url).read())['response']['docs'][0]

                speaking = doc.get('speaking', [])
                quote = doc.get('quote', [])
                #doc['date'] = dateparse(doc['date'])


                for n in range(1,6):
                    add = lxml.etree.Element('add')

                    #ngrams = defaultdict(int)
                    for index, ngram in enumerate(self.make_ngrams(text=speaking+quote, n=n)):

                        mapping = [('id', '%s.%s.%s' % (id, n, index)),
                                   ('crdoc', doc['crdoc']),
                                   ('docid', doc['id']),
                                   ('n', n),
                                   ('ngram', ' '.join(ngram)),
                                   ('document_title', doc.get('document_title')),
                                   ('granule', re.search(r'(CREC-.*?)\.xml', doc['crdoc']).groups()[0]),
                                   ('volume', doc['volume']),
                                   ('number', doc['number']),
                                   ('date', doc['date']),
                                   ('chamber', doc.get('chamber', doc['pages'][0])),
                                   ('pages', doc['pages']),
                                   ('speaker_raw', doc.get('speaker_raw')),
                                   ('speaker_state', doc.get('speaker_state')),
                                   ('speaker_party', doc.get('speaker_party')),
                                   ('speaker_bioguide', doc.get('speaker_bioguide')),
                                   ('speaker_firstname', doc.get('speaker_firstname')),
                                   ('speaker_lastname', doc.get('speaker_lastname')),
                                   ]

                        crdoc = lxml.etree.SubElement(add, 'doc')

                        for tagname, value in mapping:
                            lxml.etree.SubElement(crdoc, 'field', {'name': tagname, }).text = str(value)

                    self.save_to_solr(lxml.etree.tostring(add))

                        #ngrams[ngram] += 1
                        #print ngram

                    #for ngram, count in ngrams.iteritems():
                    #    self.save_ngram(doc, n, ngram, count)

