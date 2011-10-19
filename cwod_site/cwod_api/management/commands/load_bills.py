import json
import time
import urllib2

from django.core.management.base import BaseCommand

from cache_document_data import opencongress_create_bill
from cwod_api.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        url = 'http://localhost:8989/solr/select?q=*:*&facet=true&facet.method=enum&facet.sort=index&facet.field=bill&indent=on&rows=0&facet.limit=-1&wt=json'
        data = json.loads(urllib2.urlopen(url).read())
        bills = data['facet_counts']['facet_fields']['bill'][::2]
        congress = 110
        for bill in bills:

            if Bill.objects.filter(bill=bill, congress=congress).count():
                print 'Skipping %s | already exists' % bill
                continue

            print bill
            time.sleep(.1)
            opencongress_create_bill(bill, congress)
