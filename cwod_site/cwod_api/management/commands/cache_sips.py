import json
import urllib2
import urllib
import re
import sys

from cwod_api.models import *

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        for congress, (server, port) in settings.SOLR_SERVERS.items():
            if congress != '111':
                continue

            for session in [1, 2, ]:
                page_ids = get_page_ids(congress, session)

                for page_id in page_ids:
                    sips = get_sips(congress, session, page_id)
                    for sip in sips:
                        print sip



def get_page_ids(congress, session):
    server, port = settings.SOLR_SERVERS[congress]
    url = 'http://%s:%s/solr/select?%s' % (server, port, urllib.urlencode(
            {'q': '(congress:%s AND session: %s)' % (congress, session),
             'facet': 'true',
             'facet.field': 'page_id',
             'facet.method': 'enum',
             'facet.sort': 'index',
             'facet.limit': -1, 
             'wt': 'json',
             }
            ))
    page_ids = json.loads(urllib2.urlopen(url).read())['facet_counts']['facet_fields']['page_id'][::2]
    return page_ids


def get_sips(congress, session, page_id):
    server, port = settings.SOLR_SERVERS[congress]
    fields = ['pentagrams',
              'quadgrams',
              'trigrams',
              'bigrams',
              'unigrams', ]
    for field in fields:
        print field, page_id
        url = 'http://%s:%s/solr/select?%s' % (server, port, urllib.urlencode(
                {'q': '(congress:%s AND session:%s AND page_id:%s)' % (congress, session, page_id),
                 'facet': 'true',
                 'facet.field': field,
                 'facet.method': 'enumtermfreq',
                 'facet.sort': 'relative',
                 'facet.limit': 100,
                 'facet.mincount': 1,
                 'wt': 'json',
                 }
                ))
        print url
        data = json.loads(urllib2.urlopen(url).read())['facet_counts']['facet_fields'][field]
        phrases = data[::2]
        pcts = data[1::2]
        yield zip(phrases, pcts)
