import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from math import ceil
from ngrams.models import NgramsByDate

def recent_top_unigrams(request):
    dates = NgramsByDate.objects.values_list('date', flat=True).order_by('-date').distinct()[:6]
    popular_unigrams = []
    for date in dates:
        popular_unigrams.append((date, NgramsByDate.objects.filter(date=date, n=1)[:10]))
    return {'recent_top_unigrams': popular_unigrams}

def search_terms(request):
    return {
        'termA': request.GET.get('terma'),
        'termB': request.GET.get('termb'),
        }

def frontend(request):
    try:
        return {
            'FRONTEND_API_KEY': settings.API_KEY,
            'BASE_URL': settings.BASE_URL,
            'API_ROOT': settings.API_ROOT,
        }
    except AttributeError:
        return {}

def tickmarks(request):
    start = settings.START_YEAR
    end = datetime.date.today().year
    years = range(start, int(end)+1)
    skip_years = ceil(len(years) / 18.0)
    ticks = [datetime.date(year, 1, 1) for i, year in enumerate(years) if not i % skip_years]

    tickmarks = {
        'chart_skip_years': skip_years,
        'chart_years': years,
        'chart_ticks': ticks,
        'chart_ticks_remainder': 0,
        }
    this_year = datetime.date(years[-1], 1, 1)
    if not ticks[-1] == this_year:
        # pull out the next-to-last year if it's only one behind this year
        if ticks[-1] + relativedelta(years=1) == this_year and skip_years > 1:
            tickmarks['chart_ticks'].pop()
            tickmarks.update(chart_ticks_remainder=1)
        tickmarks.update(chart_anchor_year=this_year)

    return tickmarks
