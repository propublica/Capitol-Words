import csv
import sys
import urllib2

from django.core.management.base import BaseCommand, CommandError

from bioguide.models import Legislator

import name_tools
from lxml.html import document_fromstring


class Command(BaseCommand):
    def handle(self, *args, **options):
        fields = ['bioguide_id', 'name', 'birth_death', 'position', 'party', 'state', 'congress', ]

        for congress in range(1, 112):
            data = 'lastname=&firstname=&position=&state=&party=&congress=%s' % str(congress)
            url = 'http://bioguide.congress.gov/biosearch/biosearch1.asp'
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req).read()
            doc = document_fromstring(response)

            for row in doc.cssselect('tr'):
                try:
                    cells = row.cssselect('td')
                    if len(cells) != 6:
                        continue

                    namecell = cells[0]
                    birth_death, position, party, state, congress = [x.text.encode('utf-8') if x.text else '' for x in cells[1:]]
                    a = namecell.cssselect('a')
                    name = None

                    if a:
                        a = a[0]
                        name = a.text
                        bioguide_id = a.values()[0].split('=')[-1]
                    else:
                        continue

                    data = {'bioguide_id': bioguide_id,
                            'birth_death': birth_death,
                            'position': position,
                            'party': party,
                            'state': state,
                            'congress': congress, }

                    data['prefix'], data['first'], data['last'], data['suffix'] = name_tools.split(name)
                    legislator = Legislator.objects.create(**data)
                    print data

                except Exception, e:
                    print Exception, e
