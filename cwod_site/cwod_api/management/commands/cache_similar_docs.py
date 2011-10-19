from operator import itemgetter
import json
import urllib2
import urllib
import datetime
import re
import sys
import time

from cwod_api.models import *
from bioguide.models import *

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import IntegrityError

from dateutil.parser import parse as dateparse 


class Command(BaseCommand):

    def handle(self, *args, **options):
        for crdoc in CRDoc.objects.all():
            if crdoc.similar_documents.count():
                continue
            print crdoc, crdoc.date, crdoc.page_id
            server, port = settings.SOLR_SERVERS[str(crdoc.congress)]
            url = 'http://%s:%s/solr/select?%s' % (
                    server,
                    port,
                    urllib.urlencode(
                        {'q': 'page_id:%s AND session:%s AND congress:%s' % (crdoc.page_id, crdoc.session, crdoc.congress),
                         'mlt': 'true',
                         'mlt.fl': 'speaking,document_title,date',
                         'mlt.mintf': 1,
                         'mlt.mindf': 1,
                         'mlt.count': 5,
                         'wt': 'json',
                         'fl': 'id,score,document_title,page_id,slug,congress,session,date',
                         #'shards': ','.join(['%s:%s/solr' % (server, port) for server, port in settings.SOLR_SERVERS.values()]),
                        })
                    )
            #print url
            try:
                results = json.loads(urllib2.urlopen(url).read())['moreLikeThis']
            except KeyError:
                print 'nothing found'
                continue

            docs = []
            for key, value in results.iteritems():
                docs += value['docs']
            docs.sort(key=itemgetter('score'), reverse=True)
            for doc in docs:
                if doc['page_id'] == crdoc.page_id and dateparse(doc['date']).date() == crdoc.date:
                    continue
                try:
                    similar_doc = CRDoc.objects.exclude(pk=crdoc.pk).get(slug=doc['slug'],
                                                    congress=doc['congress'],
                                                    page_id=doc['page_id'],
                                                    session=doc['session'])
                except CRDoc.DoesNotExist:
                    print 'Does not exist'
                    continue

                print 'saving'
                crdoc.similar_documents.add(similar_doc)
