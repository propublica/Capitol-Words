from collections import defaultdict
import datetime
import itertools
import json
import re
from operator import itemgetter
import copy

from dateutil.parser import parse as dateparse

from cwod.utils import flatten_param_dicts
from django.conf import settings
from django.contrib import messages
from django.contrib.localflavor.us.us_states import US_STATES, STATE_CHOICES, US_TERRITORIES
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import connections, DatabaseError
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.simple import direct_to_template

from bioguide.models import *
from capitolwords import capitolwords, ApiError
from ngrams.models import *
from cwod.models import *

from baseconv import base62

TERRITORY_CHOICES = ('PR', 'GU', 'MP', 'AS')

capitolwords = capitolwords(api_key=settings.SUNLIGHT_API_KEY, domain=settings.API_ROOT)

# These are used in a regular expression so must be escaped.
# From NLTK
STOPWORDS = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
             'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
             'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
             'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
             'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
             'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
             'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
             'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
             'with', 'about', 'against', 'between', 'into', 'through', 'during',
             'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
             'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
             'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
             'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
             'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
             'should', 'now', '\.', '\?', '\!' ]

PUNCTUATION = ['?', '!', '.', ',']

@login_required
def index(request):
    recent_entries = RecentEntry.objects.all()[:10]

    return render_to_response('cwod/index.html',
                              {'recent_entries': recent_entries,
                              }, context_instance=RequestContext(request))

    #return direct_to_template(request, template='index.html')

@login_required
def faster_term_detail(request, term):
    # For better URLs, replace spaces with underscores and strip trailing punctuation
    if re.search(r'\s', term) or re.search(r'[%s]$' % ''.join(PUNCTUATION), term):
        term = re.sub(r'[%s]$' % ''.join(PUNCTUATION), '', term)
        term = re.sub(r'\s', '_', term.strip())
        url = reverse('cwod_term_detail', kwargs={'term': term})
        return HttpResponsePermanentRedirect(url)

    if request.GET.get('js') == 'false':
        return term_detail(request, term)

    term = re.sub(r'_', ' ', term)

    # Recent entries
    all_entries = capitolwords.text(phrase=term, bioguide_id="['' TO *]", sort='date desc,score desc', per_page=50)

    # Only show one entry for each Congressional Record page.
    entries = []
    urls = []
    for entry in all_entries:
        if entry['origin_url'] in urls:
            continue
        urls.append(entry['origin_url'])
        entries.append(entry)

    entries = _highlight_entries(entries, term)

    uri = request.build_absolute_uri()
    if '?' in uri:
        no_js_uri = uri + '&js=false'
    else:
        no_js_uri = uri + '?js=false'

    return render_to_response('cwod/term_detail.html',
                              {'term': term,
                               'entries': entries,
                               'needs_js': True,
                               'no_js_uri': no_js_uri,
                               'state_choices': US_STATES + US_TERRITORIES,
                              }, context_instance=RequestContext(request))

@login_required
def term_detail(request, term):

    # For better URLs, replace spaces with underscores & strip trailing punctuation
    if re.search(r'\s', term) or re.search(r'[%s]$' % ''.join(PUNCTUATION), term):
        term = re.sub(r'[%s]$' % ''.join(PUNCTUATION), '', term)
        term = re.sub(r'\s', '_', term.strip())
        url = reverse('cwod_term_detail', kwargs={'term': term})
        return HttpResponsePermanentRedirect(url)

    term = re.sub(r'_', ' ', term)

    stem = request.GET.get('stem', 'false')

    # Timeline
    timeline_kwargs = {'phrase': term,
                       'granularity': 'month',
                       'percentages': 'true',
                       #'smoothing': 4,
                       'mincount': 0,
                       'stem': stem,
                       'legend': 'false', }
    timeline_url = capitolwords.timeline(**timeline_kwargs)
    timeline_kwargs.update({'split_by_party': 'true', 'legend': 'true', })
    party_timeline_url = capitolwords.timeline(**timeline_kwargs)

    # custom timeline
    custom_timeline_url = timeline_url
    party = request.GET.get('party')
    state = request.GET.get('state')
    bioguide_id = request.GET.get('bioguide_id')
    if party or state or bioguide_id:
        try:
            custom_timeline_url = capitolwords.timeline(**{'phrase': term,
                                                         'granularity': 'month',
                                                         'percentages': 'true',
                                                         'mincount': 0,
                                                         'party': party,
                                                         'state': state,
                                                         'bioguide_id': bioguide_id,
                                                         'stem': stem,
                                                         })
        except ApiError:
            custom_timeline_url = 'error'

    """
    popular_dates = sorted(capitolwords.phrase_by_date_range(phrase=term, per_page=15, sort='count', percentages='true'),
                           key=itemgetter('percentage'),
                           reverse=True)[:10]
    popular_dates = [dateparse(x['day']).date() for x in popular_dates]
    """

    # Word tree
    """
    tree = capitolwords.wordtree(phrase=term)
    tree = [x for x in tree if not re.search(r' (%s)$' % '|'.join(STOPWORDS), x['phrase']) and x['count'] > 1]
    """

    # Party pie chart
    party_pie_url = capitolwords.piechart(phrase=term,
                                          entity_type='party',
                                          labels='true')

    # Commonly said by these legislators
    legislators = capitolwords.phrase_by_entity_type('legislator', phrase=term, sort='relative', per_page=10)
    for legislator in legislators:
        legislator['legislator'] = LegislatorRole.objects.filter(bioguide_id=legislator['legislator']).order_by('-congress').select_related()[0]

    # Popularity by state
    states = capitolwords.phrase_by_entity_type('state', phrase=term, sort='relative', per_page=10)

    # Recent entries
    all_entries = capitolwords.text(phrase=term, bioguide_id="['' TO *]", sort='date desc,score desc', per_page=50)

    # Only show one entry for each Congressional Record page.
    entries = []
    urls = []
    for entry in all_entries:
        if entry['origin_url'] in urls:
            continue
        urls.append(entry['origin_url'])
        entries.append(entry)

    entries = _highlight_entries(entries, term)

    return render_to_response('cwod/term_detail.html',
                              {'term': term,
                               'timeline_url': timeline_url['url'],
                               'party_timeline_url': party_timeline_url['url'],
                               'custom_timeline_url': custom_timeline_url,
                               #'popular_dates': popular_dates,
                               'party_pie_url': party_pie_url['url'],
                               'legislators': legislators,
                               'states': states,
                               #'tree': tree,
                               'entries': entries,
                               'search': request.GET.get('search') == '1',
                               'state_choices': US_STATES + US_TERRITORIES,
                              }, context_instance=RequestContext(request))


def congress_list(request):
    return


def congress_detail(request, congress):
    return


def congress_session_detail(request, congress, session):
    return


def congress_pagerange_detail(request, congress, session, pagerange):
    return


@login_required
def legislator_list(request):
    current_legislators = LegislatorRole.objects.filter(
            end_date__gte=datetime.date.today()
        ).order_by('last', 'first', 'chamber', 'party')

    congresses = LegislatorRole.objects.filter(congress__gte=104).values_list('congress', flat=True).distinct().order_by('-congress')

    return render_to_response('cwod/legislator_list.html',
                              {'current_legislators': current_legislators,
                               #'past_legislators': past_legislators,
                               'congresses': congresses,
                               'state_choices': US_STATES + US_TERRITORIES,
                              }, context_instance=RequestContext(request))



def legislator_lookup(bioguide_id):
    legislator = capitolwords.legislators(bioguide_id=bioguide_id)
    #legislators = LegislatorRole.objects.filter(bioguide_id=bioguide_id).order_by('-congress')
    if not legislator:
        return None
    return legislator

GRAM_NAMES = ['unigrams', 'bigrams', 'trigrams', 'quadgrams', 'pentagrams', ]


@login_required
def legislator_detail(request, bioguide_id, slug=None):
    legislator = legislator_lookup(bioguide_id)
    if not legislator:
        raise Http404

    if legislator['slug'] != slug:
        return HttpResponsePermanentRedirect(reverse('cwod_legislator_detail', kwargs={'bioguide_id':bioguide_id, 'slug':legislator['slug']}))

    similar_legislators = []
    for i in get_similar_entities('bioguide', bioguide_id)[:10]:
        i['legislator'] = legislator_lookup(i['bioguide'])
        similar_legislators.append(i)

    ngrams = {}
    for n in range(1, 6):
        ngrams[GRAM_NAMES[n-1]] = capitolwords.top_phrases(
                                        entity_type='legislator',
                                        entity_value=bioguide_id,
                                        n=n,
                                        per_page=30
                                        )
    ngrams = ngrams.iteritems()

    entries = capitolwords.text(bioguide_id=bioguide_id, sort='date desc', per_page=5)

    return render_to_response('cwod/legislator_detail.html',
                              {'legislator': legislator,
                               'similar_legislators': similar_legislators,
                               'entries': entries,
                               'ngrams': ngrams,
                              }, context_instance=RequestContext(request))


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def state_list(request):
    states = []
    for abbrev, statename in (US_STATES + US_TERRITORIES):
        states.append((abbrev, statename, capitolwords.top_phrases(
                        entity_type='state',
                        entity_value=abbrev,
                        n=1,
                        per_page=5)
                      ))



    state_chunks = chunks(states, (len(states)+1)/3)

    return render_to_response('cwod/state_list.html',
                              {'state_chunks': state_chunks,
                              }, context_instance=RequestContext(request))


def _highlight_entries(entries, term):
    term_parts = [re.sub(r"'s", "(?:'s)?", part) for part in re.split(r'[\s\-]', term)]
    exp = r'[\s\-%s]+?' % ''.join(PUNCTUATION)
    term = r'(?<=\b)%s(?=\b)' % exp.join(term_parts)
    for entry in entries:
        match = None
        for graf in entry['speaking']:
            graf = graf.replace('\n', '')
            versions_of_term = re.findall(term, graf, re.I)
            if versions_of_term:
                match = re.sub(r'(?<=\b)(%s)(?=\b)' % '|'.join([x for x in set(versions_of_term)]),
                               r'<em>\1</em>', graf)
                break
        entry['match'] = match
    return entries


def all_popular_terms(entity_type, entity, limit=50):
    terms = []
    for i in range(1, 6):
        terms += get_popular_ngrams(i, entity_type, entity, limit)
    return sorted(terms, key=itemgetter('tfidf'), reverse=True)


def get_popular_ngrams(n, entity_type, entity, limit=50):
    cursor = connections['ngrams'].cursor()
    table = 'tfidf__%sgrams__%s' % (['uni', 'bi', 'tri', 'quad', 'penta'][n-1], entity_type)
    try:
        cursor.execute("SELECT * FROM %s left outer join stopwords on word = ngram WHERE word is null and %s = %%s order by tfidf*(diversity+1) desc limit %s" % (table, entity_type, limit), [entity, ])
    except DatabaseError:
        return []
    fields = [x[0] for x in cursor.description]
    return [dict(zip(fields, x)) for x in cursor.fetchall()]


def get_similar_entities(entity_type, entity):
    return capitolwords._similar(entity_type=entity_type, entity_value=entity)


@login_required
def state_detail(request, state):
    state_name = dict(STATE_CHOICES + TERRITORY_CHOICES).get(state)
    if not state_name:
        raise Http404

    entries = capitolwords.text(state='"%s"' % state, sort='date desc,score desc', per_page=5)
    ngrams = {}
    for n in range(1, 6):
        ngrams[GRAM_NAMES[n-1]] = capitolwords.top_phrases(
                                        entity_type='state',
                                        entity_value=state,
                                        n=n,
                                        per_page=30
                                        )
    ngrams = ngrams.iteritems()

    similar_states = get_similar_entities('state', state)

    #legislators = LegislatorRole.objects.filter(state=state, end_date__gte=datetime.date.today()).order_by('last')
    legislators = capitolwords.legislators(state=state, congress=112)

    def sort_districts(x, y):
        try:
            x_district = int(x['district'])
        except ValueError:
            x_district = 0
        try:
            y_district = int(y['district'])
        except ValueError:
            y_district = 0
        return cmp(x_district, y_district)

    legislators = sorted(legislators, sort_districts)

    bodies = {'House': [], 'Senate': [], }
    for legislator in legislators:
        if legislator['chamber'] == 'Senate':
            bodies['Senate'].append(legislator)
        else:
            bodies['House'].append(legislator)

    bodies = sorted(bodies.items(), key=itemgetter(0), reverse=True)


    return render_to_response('cwod/state_detail.html',
            {'state': state,
             'state_name': state_name,
             'entries': entries,
             'ngrams': ngrams,
             #'other_states': other_states,
             'similar_states': similar_states,
             'bodies': bodies,
             }, context_instance=RequestContext(request))

@login_required
def submit_feedback(request):
    if request.POST:
        name = request.POST.get('feedback[name]')
        email = request.POST.get('feedback[email]')
        message = request.POST.get('feedback[message]')
        if name and email and message:
            subject = "[Capitol Words] Contact from %s" % email
            if send_mail(subject, message, '%s <%s>' % (name, settings.EMAIL_FROM), [admin[1] for admin in settings.ADMINS]):
                messages.add_message(request, messages.SUCCESS, 'Thanks, your message was sent.')
            else:
                messages.add_message(request, messages.ERROR, 'There was an error sending your message.')
        else:
            messages.add_message(request, messages.ERROR, 'Please fill out all fields and try again.')

    return render_to_response('cwod/contact.html', {}, context_instance=RequestContext(request))

def party_list(request):
    return


def party_detail(request, party):
    return


def wordtree(request):
    return


@login_required
def date_detail(request, year, month, day):
    date = datetime.date(year=int(year), month=int(month), day=int(day))
    entries = entries_for_date(date)
    print entries
    if not entries:
        raise Http404

    ngrams = {}
    for n in range(1, 6):
        ngrams[GRAM_NAMES[n-1]] = capitolwords.top_phrases(
                                        entity_type='date',
                                        entity_value=date,
                                        n=n,
                                        per_page=30,
                                        )
    ngrams = ngrams.iteritems()

    by_chamber = {'House': [], 'Senate': [], 'Extensions of Remarks': [], }
    similar_dates = get_similar_entities('date', date)

    return render_to_response('cwod/date_detail.html',
                              {'date': date,
                               'ngrams': ngrams,
                               'entries': entries,
                               'similar_dates': similar_dates,
                              }, context_instance=RequestContext(request))


def get_similar_dates(date):
    cursor = connections['ngrams'].cursor()
    cursor.execute("SELECT b FROM distance_date WHERE a = %s AND cosine_distance != 1 ORDER BY cosine_distance DESC", [date, ])
    return [x[0] for x in cursor.fetchall()]


def entries_for_date(date):
    page = 0
    chambers = {'Extensions': defaultdict(set),
                'House': defaultdict(set),
                'Senate': defaultdict(set)}
    has_entries = False
    while True:
        response = capitolwords.text(date=date, sort='id desc', page=page)

        if response and not has_entries:
            has_entries = True

        for entry in response:
            try:
                chambers[entry['chamber']][(entry['title'], entry['pages'], entry['origin_url'], entry['speaking'][0])].add(entry['speaker_last'])
            except KeyError:
                chambers[entry['chamber']][(entry['title'], entry['pages'], entry['origin_url'], '')].add(entry['speaker_last'])
            except KeyError:
                continue
        if len(response) < 50:
            break
        page += 1

    if not has_entries:
        return []

    chambers['Extensions of Remarks'] = chambers['Extensions']
    del(chambers['Extensions'])
    for k, v in chambers.iteritems():
        chambers[k] = sorted(v.items(), lambda x, y: cmp(x[0][1], y[0][1]))
    return chambers.items()


def get_similar_entries(chunks, num=10):
    to_use = sorted([x for x in chunks if x.get('bioguide_id')], lambda x, y: cmp(len(x['speaking']), len(y['speaking'])), reverse=True)

    similar = []
    for chunk in to_use[:5]:
        chunk_id = '%s.chunk%s' % (re.search(r'html\/(CREC.*?)\.', chunk['origin_url']).groups()[0], chunk['order'])
        similar += capitolwords.similar(id=chunk_id)

    # Don't show the entry we're getting similar entries for.
    similar = [x for x in similar if x['origin_url'] != chunk['origin_url']]
    similar.sort(key=itemgetter('score'), reverse=True)

    return similar[:num]


def entry_detail(request, year, month, day, page_id, slug):
    date = datetime.date(year=int(year), month=int(month), day=int(day))
    chunks = []
    page = 0
    while True:
        response = capitolwords.text(date=date, page_id=page_id, sort='id asc', page=page)
        chunks += response
        if len(response) < 1000:
            break
        page += 1

    chunks.sort(key=itemgetter('order'))

    similar_entries = get_similar_entries(chunks)

    metadata = chunks[0]
    year, month, day = [int(x) for x in metadata['date'].split('-')]
    metadata['date'] = datetime.date(year=year, month=month, day=day)

    return render_to_response('cwod/entry_detail.html',
                              {'date': date,
                               'page_id': page_id,
                               'chunks': chunks,
                               'metadata': metadata,
                               #'entries': entries_for_date(date),
                               'similar_entries': similar_entries,
                               }, context_instance=RequestContext(request))

@login_required
def search(request):
    #return HttpResponse(request.GET.get('term', ''))
    term = request.GET.get('term', '')
    url = reverse('cwod_term_detail', kwargs={'term': term}) + '?search=1'
    return HttpResponsePermanentRedirect(url)


@login_required
def term_compare(request):
    #pieces = request.path.split('/')[1:]
    return render_to_response('cwod/compare.html',
                              {},
                              context_instance=RequestContext(request))

MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December',]

@login_required
def calendar(request):
    raw_months = capitolwords._month_list()
    max_year = max(raw_months) / 100
    min_year = 1+(min(raw_months) / 100)

    # this is embarrassing
    months = []
    for m in raw_months:
        months.append(str(m))

    empty_year = []
    for i, n in enumerate(MONTH_NAMES):
        empty_year.append(["%02d" % (i+1), n, False])

    # fill out the months in every year
    years = {}
    for y in range(min_year, max_year+1):
        years[str(y)] = copy.deepcopy(empty_year)

    # activate the, um, active months
    for m in months:
        ky = m[:4]
        km = int(m[-2:])-1
        if years.has_key(ky):
            years[ky][km][2] = True

    years = sorted(years.items(), key=lambda x: int(x[0]) * -1)

    return render_to_response('cwod/calendar.html',
                              {'years': years,},
                              context_instance=RequestContext(request))

@login_required
def month_detail(request, year, month):
    year_month = '%s%s' % (year, month)
    month_name = MONTH_NAMES[int(month)-1]

    ngrams = {}
    for n in range(1, 6):
        ngrams[GRAM_NAMES[n-1]] = capitolwords.top_phrases(
                                        entity_type='month',
                                        entity_value=year_month,
                                        n=n,
                                        per_page=30
                                        )
    ngrams = ngrams.iteritems()

    dates = capitolwords._dates_in_month(year=year, month=month)

    def date_str_to_date(date_str):
        year, month, day = map(int, date_str.split('-'))
        return datetime.date(year, month, day)

    dates_by_week = [(weeknum, list(dates)) for weeknum, dates in itertools.groupby(dates, lambda x: date_str_to_date(x['date']).strftime('%U'))]

    return render_to_response('cwod/month_detail.html',
                              {'month_name': month_name,
                               'year': year,
                               'ngrams': ngrams,
                               'dates_by_week': dates_by_week,
                              },
                              context_instance=RequestContext(request))


def decode_embed(request, code):
    pk = base62.to_decimal(code)
    try:
        obj = Embed.objects.get(pk=pk)
    except Embed.DoesNotExist:
        raise Http404

    return render_to_response('cwod/embed.html', {'embed': obj}, context_instance=RequestContext(request))


def encode_embed(request):
    allowed_keys = [
        'img_src',
        'overall_img_src',
        'by_party_img_src',
        'url',
        'title',
        'chart_type',
        'chart_color',
        'start_date',
        'end_date',
        'extra',]

    defaults = {
        'extra': '{}',
        'img_src': '',
        'overall_img_src': '',
        'by_party_img_src': '',
    }

    if request.method == 'POST':
        # hack square braced keys into dicts
        post = flatten_param_dicts(request.POST.copy(), allowed_keys)
        # sanitize dates to be parseable
        try:
            start = post['start_date']
            post['start_date'] = "%s-%s-01" % (start[0:4], start[4:6])
        except KeyError:
            pass
        try:
            end = post['end_date']
            post['end_date'] = "%s-%s-01" % (end[0:4], end[4:6])
        except KeyError:
            pass
        print post['start_date']
        print post['end_date']
        values = dict([(k,v) for k, v in post.items() if k in allowed_keys])
        values.update(defaults=defaults)
        obj, created = Embed.objects.get_or_create(**values)
        values.pop('defaults')
        # un-clobber passed in values clobbered by defaults
        obj.__dict__.update(**values)
        obj.save()
        return HttpResponse(obj.js_url())

    return HttpResponse('')


def js_embed(request):
    code = request.GET.get('c')
    if not code:
        raise Http404
    return render_to_response('cwod/embed.js',
                              {'code': code},
                              mimetype='text/javascript',
                              )