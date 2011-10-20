import re

from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.defaultfilters import slugify

def get_entry_detail_url(origin_url, title):
    crec = origin_url.split('/')[-1].replace('.htm', '')
    m = re.search(r'CREC-(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d)-pt\d-Pg(?P<page_id>.*?)$', crec)
    if not m:
        return ''
    kwargs = m.groupdict()
    kwargs['slug'] = slugify(title)[:50]
    try:
        url = reverse('cwod_entry_detail', kwargs=kwargs)
    except NoReverseMatch:
        url = ''
    return url