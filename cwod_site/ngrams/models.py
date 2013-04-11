import datetime

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.localflavor.us.us_states import US_STATES as STATES_TUPLE

from bioguide.models import Legislator

STATES_DICT = dict(STATES_TUPLE)

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


class NgramsByYear(models.Model):
    n = models.IntegerField()
    year = models.CharField(max_length=4)
    ngram = models.CharField(max_length=255)
    tfidf = models.FloatField()
    count = models.IntegerField()

    class Meta:
        ordering = ['-tfidf', '-count', ]

    def __unicode__(self):
        return self.ngram

    def pct(self):
        top = NgramsByYear.objects.filter(year=self.year).values_list('tfidf', flat=True)[0]
        return (self.tfidf / top) * 100

    def ngram_pct(self):
        top = NgramsByYear.objects.filter(year=self.year, n=self.n).values_list('tfidf', flat=True)[0]
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
    a = models.DateField(db_index=True)
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

class DistanceMonth(models.Model):
    a = models.PositiveIntegerField(db_index=True)
    b = models.PositiveIntegerField()
    cosine_distance = models.FloatField()

    class Meta:
        ordering = ['-cosine_distance', ]
        db_table = 'distance_month'

    def __unicode__(self):
        year = int(str(self.b)[0:4])
        month = int(str(self.b)[4:6])
        date = datetime.date(year, month, 1)
        return date.strftime('%B %Y')

    @models.permalink
    def get_absolute_url(self):
        return ('cwod_month_detail', [str(self.b)[0:4],
                                      str(self.b)[4:6], ])

class DistanceState(models.Model):
    a = models.CharField(max_length=2, db_index=True)
    b = models.CharField(max_length=2)
    cosine_distance = models.FloatField()

    class Meta:
        ordering = ['-cosine_distance', ]
        db_table = 'distance_state'

    def __unicode__(self):
        try:
            return STATES_DICT[self.b]
        except KeyError:
            return self.b

    @models.permalink
    def get_absolute_url(self):
        return ('cwod_state_detail', [self.b, ])

class DistanceBioguide(models.Model):
    a = models.CharField(max_length=8, db_index=True)
    b = models.CharField(max_length=8)
    cosine_distance = models.FloatField()

    class Meta:
        ordering = ['-cosine_distance', ]
        db_table = 'distance_bioguide'

    def __unicode__(self):
        try:
            leg = Legislator.objects.get(bioguide_id=self.b)
            return leg.__unicode__()
        except Legislator.DoesNotExist:
            return self.b

    @models.permalink
    def get_absolute_url(self):
        return ('cwod_legislator_detail', [self.b, ])
