import json
import time
import urllib2

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.conf import settings

from bioguide.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        bioguide_ids = Legislator.objects.order_by('bioguide_id').values_list('bioguide_id', flat=True).distinct()
        for bioguide_id in bioguide_ids:
            if LegislatorRole.objects.filter(bioguide_id=bioguide_id).count() > 0:
                continue

            url = 'http://api.nytimes.com/svc/politics/v3/us/legislative/congress/members/%s.json?api-key=%s' % (bioguide_id, settings.NYT_API_KEY)
            try:
                data = json.loads(urllib2.urlopen(url).read())
            except urllib2.HTTPError:
                print
                print 'URL NOT FOUND FOR: %s' % bioguide_id
                print
                continue
            result = data['results'][0]
            roles = result['roles']
            for role in roles:
                print role
                try:
                    LegislatorRole.objects.create(
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

            time.sleep(.55)

