"""Cache data such as document titles and slugs
from Solr.
"""
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
from django.template.defaultfilters import slugify

from dateutil.parser import parse as dateparse 


class Command(BaseCommand):

    def handle(self, *args, **options):
        fields = ['slug', 'page_id', 'document_title',
                  'congress','session', 'date', ]

        for congress, (server, port) in settings.SOLR_SERVERS.items():
            for session in [1, 2, ]:
                if congress == '111':
                    continue

                url = 'http://%s:%s/solr/select?%s' % (server,
                                                       port,
                                                       urllib.urlencode({'q': '(congress:%s AND session:%s)' % (congress, session),
                                                                         'rows': 0,
                                                                         'facet': 'true',
                                                                         'facet.field': 'page_id',
                                                                         'facet.method': 'enum',
                                                                         'facet.limit': -1,
                                                                         'facet.mincount': 1,
                                                                         'wt': 'json', })
                                                       )
                page_ids = json.loads(urllib2.urlopen(url).read())['facet_counts']['facet_fields']['page_id'][::2]
                for page_id in page_ids:
                    if CRDoc.objects.filter(page_id=page_id, session=session, congress=congress).count():
                        continue
                    url = 'http://%s:%s/solr/select?%s' % (server,
                                                           port,
                                                           urllib.urlencode({'q': '(page_id:%s AND congress:%s AND session:%s)' % (page_id, congress, session),
                                                                             'rows': 1,
                                                                             'wt': 'json', 
                                                                             'fl': ','.join(fields),
                                                                             })
                            )
                    result = json.loads(urllib2.urlopen(url).read())

                    try:
                        data = result['response']['docs'][0]
                    except (KeyError, IndexError):
                        print 'ERROR: %s %s %s' % (congress, session, page_id)

                    chamber = {'E': 'Extensions of Remarks',
                               'H': 'House',
                               'S': 'Senate', }.get(page_id[0])
                    data['chamber'] = chamber
                    if not chamber:
                        continue
                    print 'original date: %s' % data['date']
                    data['date'] = dateparse(data['date'])

                    doc, created = CRDoc.objects.get_or_create(**data)

                    print doc

                    # Get speakers and bills
                    url = 'http://%s:%s/solr/select?%s' % (server,
                                                           port,
                                                           urllib.urlencode({'q': '(page_id:%s AND congress:%s AND session:%s)' % (page_id, congress, data['session']),
                                                                             'rows': result['response']['numFound'],
                                                                             'wt': 'json',
                                                                             'fl': 'speaker_bioguide,bill', })
                                                           )
                    print url
                    result = json.loads(urllib2.urlopen(url).read())

                    # speakers
                    bioguide_ids = set([x.get('speaker_bioguide') 
                                            for x in result['response']['docs'] 
                                                if x.get('speaker_bioguide')])
                    for bioguide_id in bioguide_ids:
                        print page_id, bioguide_id, data['date']
                        try:
                            legislator = LegislatorRole.objects.filter(bioguide_id=bioguide_id,
                                                                    begin_date__lte=data['date'],
                                                                    end_date__gte=data['date'])[0]
                        except IndexError:
                            continue
                        doc.legislators.add(legislator)

                    continue

                    # bills
                    bills = x.get('bill', [])

                    for bill in bills:
                        try:
                            bill_obj = Bill.objects.get(bill=bill,
                                                        congress=congress)
                        except Bill.DoesNotExist:
                            if int(congress) >= 109:
                                bill_obj = opencongress_create_bill(bill, congress)

                        print
                        print bill_obj
                        if bill_obj:
                            doc.bills.add(bill_obj)


def opencongress_create_bill(bill, congress):
    slug = slugify(bill)
    billtype, number = re.split(r'\.\d', re.sub(r'\s', '', bill))
    try:
        billtype = {'H.R': 'h',
                    'H': 'h',
                    'S': 's',
                    'H.J': 'hj',
                    'H.J.Res': 'hj',
                    'S.J.Res': 'sj',
                    'H.Res': 'hr',
                    'H.Con.Res': 'hc',
                    'S.Con.Res': 'sc',
                    'S.Res': 'sr',
                    'S.R': 's', }[billtype]
    except KeyError:
        return

    url = 'http://www.opencongress.org/api/bills?%s' % urllib.urlencode({'number': number,
                                                                         'type': billtype,     
                                                                         'congress': congress,
                                                                         'format': 'json',
                                                                         'key': settings.OPENCONGRESS_API_KEY, })

    try:
        response = json.loads(urllib2.urlopen(url).read())
    except urllib2.HTTPError:
        return
    if not 'bills' in response:
        return
    item = response['bills'][0]
    if not item:
        return

    sponsor = item.get('sponsor')
    cosponsors = item.get('co_sponsors')
    actions = item['most_recent_actions']
    last_action = actions[0]
    last_action_date = datetime.date.today() - datetime.timedelta(seconds=time.time() - actions[0]['date'])
    summary = item['plain_language_summary'] or item['summary']
    title = item['title_full_common']
    introduced = datetime.date.today() - datetime.timedelta(seconds=time.time() - item['introduced'])

    try:
        sponsor = LegislatorRole.objects.filter(bioguide_id=sponsor['bioguideid'],
                        begin_date__lte=introduced,
                        end_date__gte=introduced)[0]
    except IndexError:
        sponsor = None

    bill_obj = Bill.objects.create(slug=slug,
                                   bill=bill,
                                   congress=congress,
                                   bill_title=title,
                                   last_action=last_action['text'] or '',
                                   last_action_date=last_action_date,
                                   sponsor=sponsor,
                                   summary=summary,
                                   url='http://www.opencongress.org/bill/%s-%s%s/show' % (congress,
                                                                                          item['bill_type'],
                                                                                          item['number']),
                                   source='OpenCongress'
                                   )

    for cosponsor in cosponsors:
        try:
            cosponsor_obj = LegislatorRole.objects.filter(bioguide_id=cosponsor['bioguideid'],
                            begin_date__lte=introduced,
                            end_date__gte=introduced)[0]
        except IndexError:
            continue
        bill_obj.cosponsors.add(cosponsor_obj)

    time.sleep(.25)

    return bill_obj
