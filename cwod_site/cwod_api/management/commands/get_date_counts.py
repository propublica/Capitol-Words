from optparse import make_option
import os
import datetime
import json
import urllib
import urllib2

from django.core.management.base import BaseCommand
from cwod_api.models import NgramDateCount
from ngrams.models import Date

from dateutil.parser import parse as dateparse


class DateCounter(object):

    fields = ['unigrams', 'bigrams', 'trigrams', 'quadgrams',
              'pentagrams', ]

    def dates(self, start, end):
        curr = start
        while True:
            yield curr
            if curr == end:
                break
            curr += datetime.timedelta(1)

    def make_path(self, date):
        root = '/opt/data/solrdocs'
        return os.path.join(root, str(date.year), date.strftime('%m'), date.strftime('%d'))

    def count(self, field, date):
        path = self.make_path(date)
        all_filename = 'all-%s-%s-%s.xml' % (date.year, date.strftime('%m'), date.strftime('%d'))
        if os.path.exists(path):
            result = os.popen('''grep '"%s">' %s | wc -l''' % (field, os.path.join(path, 'CREC*.xml')))
            return int(list(result)[0].strip())
        return 0


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
            make_option('--date',
                action='store',
                dest='date',
                default=None,
                help='Date for which to store the number of ngrams'),
            make_option('--start_date',
                action='store',
                dest='start_date',
                default=None,
                help='Date for which to store the number of ngrams'),
            make_option('--end_date',
                action='store',
                dest='end_date',
                default=None,
                help='Date for which to store the number of ngrams'),
            make_option('--n',
                action='store',
                dest='n',
                default=None,
                help='Size of phrase for which to store date data'),
            )

    def handle(self, *args, **options):
        date = options.get('date')
        start_date = options.get('start_date')
        end_date = options.get('end_date')
        n = options.get('n')

        counter = DateCounter()

        if n:
            n = int(n)
            enumerator = [(n, counter.fields[n-1]),]
        else:
            enumerator = list(enumerate(counter.fields))

        dates = []
        if date:
            dates = [dateparse(date).date(),]
        elif start_date and end_date:
            dates = counter.dates(dateparse(start_date).date(), dateparse(end_date).date())
        elif start_date and not end_date:
            dates = counter.dates(dateparse(start_date).date(), datetime.date.today())
        else:
            dates = counter.dates(datetime.date(2009, 1, 1), datetime.date.today())

        for date in dates:
            for n, field in enumerator:
                print date, n, field
                num = counter.count(field, date)
                if num == 0:
                    continue
                ngramcount, created = NgramDateCount.objects.get_or_create(n=n,
                                                                           date=date,
                                                                           defaults={'count': 0})
                ngramcount.count = num
                ngramcount.save()
                print date, field, num

                d = Date.objects.get_or_create(date=date)
