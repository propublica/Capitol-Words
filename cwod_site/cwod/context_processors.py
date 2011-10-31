from django.conf import settings
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

def frontend_apikey(request):
    try:
        return {'FRONTEND_API_KEY': settings.FRONTEND_API_KEY}
    except AttributeError:
        return {}