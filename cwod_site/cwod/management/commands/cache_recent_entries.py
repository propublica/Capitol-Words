"""Generate a list of entries with multiple speakers
to show on the homepage.
"""
import pprint
import re

from ngrams.models import Date
from cwod.views import entries_for_date
from cwod.templatetags.capwords import smart_title
from cwod.models import RecentEntry

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.utils import IntegrityError


def entry_detail_pieces(origin_url, title):
    crec = origin_url.split('/')[-1].replace('.htm', '')
    m = re.search(r'CREC-(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d)-pt\d-Pg(?P<page_id>.*?)$', crec)
    if not m:
        return None
    kwargs = m.groupdict()
    kwargs['slug'] = slugify(title)[:50]
    kwargs['title'] = smart_title(title)
    return kwargs
    try:
        url = reverse('cwod_entry_detail', kwargs=kwargs)
    except NoReverseMatch:
        return None
    return url

def page_id(origin_url):
    crec = origin_url.split('/')[-1].replace('.htm', '')
    m = re.search(r'CREC-\d{4}-\d\d-\d\d-pt\d-Pg(?P<page_id>.*?)$', crec)
    return m.groupdict()['page_id']


class Command(BaseCommand):

    def handle(self, *args, **options):
        pp = pprint.PrettyPrinter(indent=4)

        date = Date.objects.order_by('-date')[0]
        chamber_entries = entries_for_date(date.date)

        entries = sum([x[1] for x in chamber_entries], [])
        entries.sort(lambda x, y: cmp(len(x[-1]), len(y[-1])), reverse=True)

        for entry_details, speakers in entries[:10]:
            title, pagenum, origin_url, excerpt = entry_details
            kwargs = {'date': date.date,
                      'title': smart_title(title),
                      'slug': slugify(title)[:50],
                      'num_speakers': len(speakers),
                      'page_id': page_id(origin_url), }

            try:
                entry = RecentEntry.objects.create(**kwargs)
            except IntegrityError:
                continue
