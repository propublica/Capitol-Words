from ngrams.models import NgramsByDate

def recent_top_unigrams(request):
    dates = NgramsByDate.objects.values_list('date', flat=True).order_by('-date').distinct()[:6]
    popular_unigrams = []
    for date in dates:
        popular_unigrams.append((date, NgramsByDate.objects.filter(date=date, n=1)[:5]))
    return {'recent_top_unigrams': popular_unigrams}
