import datetime
import re

from django.conf import settings
from django.contrib.localflavor.us.us_states import US_STATES
from django.core.urlresolvers import reverse, NoReverseMatch
from django import template
from django.template.defaultfilters import slugify

from dateutil.parser import parse as dateparse

from bioguide.models import *

register = template.Library()

@register.filter(name='underscorify')
def underscorify(s):
    return re.sub(r'\s+', '_', s)


@register.filter(name='divided_by')
def divided_by(n, d):
    try:
        return (float(n) / float(d)) * 100
    except Exception, e:
        return 0

@register.filter(name='to_list')
def to_list(s):
    return list(s)


@register.filter(name='remove_nones')
def remove_nones(l):
    return [x for x in l if x is not None]

@register.filter(name='date_parse')
def date_parse(s):
    try:
        return dateparse(s)
    except:
        return ''


@register.filter(name='smart_title')
def smart_title(s):
    s = s.title()
    to_uppercase = ['Gop', ]
    regex = re.compile(r'(%s)' % '|'.join([r'\b%s\b' % x for x in to_uppercase]))
    return regex.sub(lambda x: x.group().upper(), s)


@register.filter(name='legislator_lookup')
def legislator_lookup(chunk):
    from cwod.capitolwords import capitolwords, ApiError
    capitolwords = capitolwords(api_key=settings.SUNLIGHT_API_KEY, domain=settings.API_ROOT)
    legislator = capitolwords.get_legislator(congress=chunk.get('congress'), bioguide_id=chunk.get('bioguide_id'))
    return legislator['results']
    if isinstance(chunk['date'], str):
        year, month, day = [int(x) for x in chunk['date'].split('-')]
        date = datetime.date(year, month, day)
    else:
        date = chunk['date']
    roles = LegislatorRole.objects.filter(bioguide_id=chunk['bioguide_id'],
                                         begin_date__lte=date,
                                         end_date__gte=date)
    if roles:
        return roles[0]

    roles = LegislatorRole.objects.filter(bioguide_id=chunk['bioguide_id']).order_by('-end_date')
    if roles:
        return roles[0]

    return {}


@register.filter(name='state_abbrev_to_full')
def state_abbrev_to_full(abbrev):
    return dict(US_STATES).get(abbrev, abbrev)


@register.filter(name='state_abbrev_to_ap')
def state_abbrev_to_ap(abbrev):
    return AP_STATES.get(abbrev, abbrev)

@register.filter(name='decimal_to_percent')
def decimal_to_percent(n):
    return n*100


@register.filter(name='party_initial_to_abbrev')
def party_initial_to_abbrev(initial):
    initials = {
        'D': 'Dem',
        'R': 'Rep',
        'I': 'Ind',
    }
    try:
        initial = initials[initial]
    except KeyError:
        pass
    return initial


@register.tag(name='legislator_thumbnail')
def legislator_thumbnail(parser, token):
    try:
        tag_name, bioguide_id, size = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires a two arguments' % token.contents.split()[0])
    return LegislatorThumbnailNode(bioguide_id, size)


class LegislatorThumbnailNode(template.Node):
    def __init__(self, bioguide_id, size):
        self.bioguide_id = template.Variable(bioguide_id)
        self.size = size

    def render(self, context):
        bioguide_id = self.bioguide_id.resolve(context)
        return 'http://assets.sunlightfoundation.com/moc/%s/%s.jpg' % (self.size, bioguide_id)


@register.tag(name='entry_detail_url')
def entry_detail_url(parser, token):
    try:
        tag_name, origin_url, title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires two arguments' % token.contents.split()[0])
    return EntryDetailUrlNode(origin_url, title)

class EntryDetailUrlNode(template.Node):
    def __init__(self, origin_url, title):
        self.origin_url = template.Variable(origin_url)
        self.doc_title = template.Variable(title)

    def render(self, context):
        origin_url = self.origin_url.resolve(context)
        title = self.doc_title.resolve(context)
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

