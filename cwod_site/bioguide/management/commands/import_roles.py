import time

import requests

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.conf import settings

from cwod_site.bioguide.models import Legislator, LegislatorRole

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            congress = args[0]
        except IndexError:
            congress = None
        bioguide_ids = Legislator.objects.order_by('bioguide_id').values_list('bioguide_id', flat=True).distinct()

        s = requests.Session()
        s.headers.update({'X-API-Key': settings.PROPUBLICA_API_KEY})
        for bioguide_id in bioguide_ids:
            # if LegislatorRole.objects.filter(bioguide_id=bioguide_id).count() > 0:
            #     continue

            url = 'https://api.propublica.org/congress/v1/members/{}.json'.format(bioguide_id)
            try:
                data = s.get(url).json()
            except Exception, e:
                print
                print "CAUGHT ERROR FOR %s: %s" % (bioguide_id, e)
                print
                continue

            if data['status'].upper() == 'ERROR':
                print
                print "API Responded with error for %s, %s" % (url, data['errors'])
                print
                continue

            result = data['results'][0]
            roles = result['roles']
            for role in roles:
                if congress and int(role['congress']) != int(congress):
                    continue
                print role
                try:
                    LegislatorRole.objects.get_or_create(
                            bioguide_id=bioguide_id,
                            first=result['first_name'],
                            middle=result['middle_name'],
                            last=result['last_name'],
                            congress=role['congress'],
                            chamber=role['chamber'],
                            party=role['party'],
                            title=role['title'],
                            state=role['state'],
                            district=role['district'],
                            begin_date=role['start_date'],
                            end_date=role['end_date'])
                except IntegrityError:
                    continue

            time.sleep(0.1)

        s.close()
