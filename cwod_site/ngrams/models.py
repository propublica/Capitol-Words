from django.db import models
from django.core.urlresolvers import reverse


class Date(models.Model):
    date = models.DateField()

    @models.permalink
    def get_absolute_url(self):
        return ('cwod_date_detail', [self.date.strftime('%Y'),
                                     self.date.strftime('%m'),
                                     self.date.strftime('%d'), ])


class NgramsByState(models.Model):
    n = models.IntegerField()
    state = models.CharField(max_length=2)
    ngram = models.CharField(max_length=255)
    tfidf = models.FloatField()
    count = models.IntegerField()

    class Meta:
        ordering = ['-tfidf', '-count', ]

    def __unicode__(self):
        return self.ngram

    def pct(self):
        top = NgramsByState.objects.filter(state=self.state).values_list('tfidf', flat=True)[0]
        return (self.tfidf / top) * 100

    def ngram_pct(self):
        top = NgramsByState.objects.filter(state=self.state, n=self.n).values_list('tfidf', flat=True)[0]
        return (self.tfidf / top) * 100

class NgramsByBioguide(models.Model):
    n = models.IntegerField()
    bioguide_id = models.CharField(max_length=7)
    ngram = models.CharField(max_length=255)
    tfidf = models.FloatField()
    count = models.IntegerField()

    class Meta:
        ordering = ['-tfidf', '-count', ]

    def __unicode__(self):
        return self.ngram

    def pct(self):
        top = NgramsByBioguide.objects.filter(bioguide_id=self.bioguide_id).values_list('tfidf', flat=True)[0]
        return (self.tfidf / top) * 100

    def ngram_pct(self):
        top = NgramsByBioguide.objects.filter(bioguide_id=self.bioguide_id, n=self.n).values_list('tfidf', flat=True)[0]
        return (self.tfidf / top) * 100


class NgramsByDate(models.Model):
    n = models.IntegerField()
    date = models.DateField()
    ngram = models.CharField(max_length=255)
    tfidf = models.FloatField()
    count = models.IntegerField()

    class Meta:
        ordering = ['-tfidf', '-count', ]

    def __unicode__(self):
        return self.ngram

    def pct(self):
        top = NgramsByDate.objects.filter(date=self.date).values_list('tfidf', flat=True)[0]
        return (self.tfidf / top) * 100

    def ngram_pct(self):
        top = NgramsByDate.objects.filter(date=self.date, n=self.n).values_list('tfidf', flat=True)[0]
        return (self.tfidf / top) * 100

    @models.permalink
    def date_url(self):
        return ('cwod_date_detail', [self.date.strftime('%Y'),
                                     self.date.strftime('%m'),
                                     self.date.strftime('%d'), ])



class NgramsByMonth(models.Model):
    n = models.IntegerField()
    month = models.CharField(max_length=6)
    ngram = models.CharField(max_length=255)
    tfidf = models.FloatField()
    count = models.IntegerField()

    class Meta:
        ordering = ['-tfidf', '-count', ]

    def __unicode__(self):
        return self.ngram

    def pct(self):
        top = NgramsByMonth.objects.filter(month=self.month).values_list('tfidf', flat=True)[0]
        return (self.tfidf / top) * 100

    def ngram_pct(self):
        top = NgramsByMonth.objects.filter(month=self.month, n=self.n).values_list('tfidf', flat=True)[0]
        return (self.tfidf / top) * 100


class TopUnigrams(models.Model):
    rank = models.IntegerField()
    ngram = models.CharField(max_length=255)
    count = models.IntegerField()
    diversity = models.IntegerField()
    pct = models.FloatField()
    tfidf = models.FloatField()
    pct_times_tfidf = models.FloatField()
    diversity_times_pct_tfidf = models.FloatField()

    class Meta:
        ordering = ['-diversity_times_pct_tfidf', ]
        abstract = True

    def __unicode__(self):
        return self.ngram


class DistanceDate(models.Model):
    a = models.DateField()
    b = models.DateField()
    cosine_distance = models.FloatField()

    class Meta:
        ordering = ['-cosine_distance', ]
        db_table = 'distance_date'

    def __unicode__(self):
        return self.b.strftime('%Y-%m-%d')

    @models.permalink
    def get_absolute_url(self):
        return ('cwod_date_detail', [self.b.year,
                                     self.b.strftime('%m'),
                                     self.b.strftime('%d'), ])

