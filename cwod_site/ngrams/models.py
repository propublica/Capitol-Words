from django.db import models

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

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


class TopUnigramsByState(TopUnigrams):
    state = models.CharField(max_length=2, db_index=True)


class TopUnigramsByDate(TopUnigrams):
    date = models.DateField(db_index=True)


class TopUnigramsByBioguide(TopUnigrams):
    bioguide_id = models.CharField(max_length=7, db_index=True)


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


'''
class Bigrams(models.Model):
    id = models.IntegerField(primary_key=True)
    granule = models.CharField(max_length=600)
    page_id = models.CharField(max_length=96)
    pages = models.CharField(max_length=96)
    date = models.DateField()
    number = models.IntegerField()
    volume = models.IntegerField()
    session = models.IntegerField()
    congress = models.IntegerField()
    document_title = models.CharField(max_length=765)
    speaker_raw = models.CharField(max_length=765)
    speaker_firstname = models.CharField(max_length=765)
    speaker_lastname = models.CharField(max_length=765)
    speaker_state = models.CharField(max_length=6)
    speaker_bioguide = models.CharField(max_length=21)
    speaker_party = models.CharField(max_length=9)
    ngram = models.CharField(max_length=765)
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams'

class BigramsByCount(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count'

class BigramsByCountBioguide(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__bioguide'

class BigramsByCountBioguideCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__bioguide_congress'

class BigramsByCountBioguideDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    bioguide = models.CharField(max_length=21)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__bioguide_date'

class BigramsByCountBioguideYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__bioguide_year'

class BigramsByCountChamber(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber'

class BigramsByCountChamberCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_congress'

class BigramsByCountChamberCongressParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_congress_party'

class BigramsByCountChamberCongressPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_congress_party_state'

class BigramsByCountChamberDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_date'

class BigramsByCountChamberDateParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_date_party'

class BigramsByCountChamberDatePartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_date_party_state'

class BigramsByCountChamberParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_party'

class BigramsByCountChamberPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_party_state'

class BigramsByCountChamberPartyStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_party_state_year'

class BigramsByCountChamberPartyYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_party_year'

class BigramsByCountChamberState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_state'

class BigramsByCountChamberYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__chamber_year'

class BigramsByCountCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__congress'

class BigramsByCountCongressParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__congress_party'

class BigramsByCountCongressPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__congress_party_state'

class BigramsByCountCongressState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__congress_state'

class BigramsByCountDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__date'

class BigramsByCountDateParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__date_party'

class BigramsByCountDatePartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__date_party_state'

class BigramsByCountDateState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__date_state'

class BigramsByCountParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__party'

class BigramsByCountPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__party_state'

class BigramsByCountPartyStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__party_state_year'

class BigramsByCountPartyYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__party_year'

class BigramsByCountState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__state'

class BigramsByCountStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__state_year'

class BigramsByCountYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'bigrams_by_count__year'

class Pentagrams(models.Model):
    id = models.IntegerField(primary_key=True)
    granule = models.CharField(max_length=600)
    page_id = models.CharField(max_length=96)
    pages = models.CharField(max_length=96)
    date = models.DateField()
    number = models.IntegerField()
    volume = models.IntegerField()
    session = models.IntegerField()
    congress = models.IntegerField()
    document_title = models.CharField(max_length=765)
    speaker_raw = models.CharField(max_length=765)
    speaker_firstname = models.CharField(max_length=765)
    speaker_lastname = models.CharField(max_length=765)
    speaker_state = models.CharField(max_length=6)
    speaker_bioguide = models.CharField(max_length=21)
    speaker_party = models.CharField(max_length=9)
    ngram = models.CharField(max_length=765)
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams'

class PentagramsByCount(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count'

class PentagramsByCountBioguide(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__bioguide'

class PentagramsByCountBioguideCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__bioguide_congress'

class PentagramsByCountBioguideDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    bioguide = models.CharField(max_length=21)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__bioguide_date'

class PentagramsByCountBioguideYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__bioguide_year'

class PentagramsByCountChamber(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber'

class PentagramsByCountChamberCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_congress'

class PentagramsByCountChamberCongressParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_congress_party'

class PentagramsByCountChamberCongressPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_congress_party_state'

class PentagramsByCountChamberDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_date'

class PentagramsByCountChamberDateParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_date_party'

class PentagramsByCountChamberDatePartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_date_party_state'

class PentagramsByCountChamberParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_party'

class PentagramsByCountChamberPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_party_state'

class PentagramsByCountChamberPartyStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_party_state_year'

class PentagramsByCountChamberPartyYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_party_year'

class PentagramsByCountChamberState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_state'

class PentagramsByCountChamberYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__chamber_year'

class PentagramsByCountCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__congress'

class PentagramsByCountCongressParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__congress_party'

class PentagramsByCountCongressPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__congress_party_state'

class PentagramsByCountCongressState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__congress_state'

class PentagramsByCountDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__date'

class PentagramsByCountDateParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__date_party'

class PentagramsByCountDatePartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__date_party_state'

class PentagramsByCountDateState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__date_state'

class PentagramsByCountParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__party'

class PentagramsByCountPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__party_state'

class PentagramsByCountPartyStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__party_state_year'

class PentagramsByCountPartyYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__party_year'

class PentagramsByCountState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__state'

class PentagramsByCountStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__state_year'

class PentagramsByCountYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'pentagrams_by_count__year'

class Quadgrams(models.Model):
    id = models.IntegerField(primary_key=True)
    granule = models.CharField(max_length=600)
    page_id = models.CharField(max_length=96)
    pages = models.CharField(max_length=96)
    date = models.DateField()
    number = models.IntegerField()
    volume = models.IntegerField()
    session = models.IntegerField()
    congress = models.IntegerField()
    document_title = models.CharField(max_length=765)
    speaker_raw = models.CharField(max_length=765)
    speaker_firstname = models.CharField(max_length=765)
    speaker_lastname = models.CharField(max_length=765)
    speaker_state = models.CharField(max_length=6)
    speaker_bioguide = models.CharField(max_length=21)
    speaker_party = models.CharField(max_length=9)
    ngram = models.CharField(max_length=765)
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams'

class QuadgramsByCount(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count'

class QuadgramsByCountBioguide(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__bioguide'

class QuadgramsByCountBioguideCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__bioguide_congress'

class QuadgramsByCountBioguideDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    bioguide = models.CharField(max_length=21)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__bioguide_date'

class QuadgramsByCountBioguideYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__bioguide_year'

class QuadgramsByCountChamber(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber'

class QuadgramsByCountChamberCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_congress'

class QuadgramsByCountChamberCongressParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_congress_party'

class QuadgramsByCountChamberCongressPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_congress_party_state'

class QuadgramsByCountChamberDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_date'

class QuadgramsByCountChamberDateParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_date_party'

class QuadgramsByCountChamberDatePartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_date_party_state'

class QuadgramsByCountChamberParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_party'

class QuadgramsByCountChamberPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_party_state'

class QuadgramsByCountChamberPartyStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_party_state_year'

class QuadgramsByCountChamberPartyYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_party_year'

class QuadgramsByCountChamberState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_state'

class QuadgramsByCountChamberYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__chamber_year'

class QuadgramsByCountCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__congress'

class QuadgramsByCountCongressParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__congress_party'

class QuadgramsByCountCongressPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__congress_party_state'

class QuadgramsByCountCongressState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__congress_state'

class QuadgramsByCountDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__date'

class QuadgramsByCountDateParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__date_party'

class QuadgramsByCountDatePartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__date_party_state'

class QuadgramsByCountDateState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__date_state'

class QuadgramsByCountParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__party'

class QuadgramsByCountPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__party_state'

class QuadgramsByCountPartyStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__party_state_year'

class QuadgramsByCountPartyYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__party_year'

class QuadgramsByCountState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__state'

class QuadgramsByCountStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__state_year'

class QuadgramsByCountYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'quadgrams_by_count__year'

class Trigrams(models.Model):
    id = models.IntegerField(primary_key=True)
    granule = models.CharField(max_length=600)
    page_id = models.CharField(max_length=96)
    pages = models.CharField(max_length=96)
    date = models.DateField()
    number = models.IntegerField()
    volume = models.IntegerField()
    session = models.IntegerField()
    congress = models.IntegerField()
    document_title = models.CharField(max_length=765)
    speaker_raw = models.CharField(max_length=765)
    speaker_firstname = models.CharField(max_length=765)
    speaker_lastname = models.CharField(max_length=765)
    speaker_state = models.CharField(max_length=6)
    speaker_bioguide = models.CharField(max_length=21)
    speaker_party = models.CharField(max_length=9)
    ngram = models.CharField(max_length=765)
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams'

class TrigramsByCount(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count'

class TrigramsByCountBioguide(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__bioguide'

class TrigramsByCountBioguideCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__bioguide_congress'

class TrigramsByCountBioguideDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    bioguide = models.CharField(max_length=21)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__bioguide_date'

class TrigramsByCountBioguideYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__bioguide_year'

class TrigramsByCountChamber(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber'

class TrigramsByCountChamberCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_congress'

class TrigramsByCountChamberCongressParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_congress_party'

class TrigramsByCountChamberCongressPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_congress_party_state'

class TrigramsByCountChamberDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_date'

class TrigramsByCountChamberDateParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_date_party'

class TrigramsByCountChamberDatePartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_date_party_state'

class TrigramsByCountChamberParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_party'

class TrigramsByCountChamberPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_party_state'

class TrigramsByCountChamberPartyStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_party_state_year'

class TrigramsByCountChamberPartyYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_party_year'

class TrigramsByCountChamberState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_state'

class TrigramsByCountChamberYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__chamber_year'

class TrigramsByCountCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__congress'

class TrigramsByCountCongressParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__congress_party'

class TrigramsByCountCongressPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__congress_party_state'

class TrigramsByCountCongressState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__congress_state'

class TrigramsByCountDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__date'

class TrigramsByCountDateParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__date_party'

class TrigramsByCountDatePartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__date_party_state'

class TrigramsByCountDateState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__date_state'

class TrigramsByCountParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__party'

class TrigramsByCountPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__party_state'

class TrigramsByCountPartyStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__party_state_year'

class TrigramsByCountPartyYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__party_year'

class TrigramsByCountState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__state'

class TrigramsByCountStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__state_year'

class TrigramsByCountYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'trigrams_by_count__year'

class Unigrams(models.Model):
    id = models.IntegerField(primary_key=True)
    granule = models.CharField(max_length=600)
    page_id = models.CharField(max_length=96)
    pages = models.CharField(max_length=96)
    date = models.DateField()
    number = models.IntegerField()
    volume = models.IntegerField()
    session = models.IntegerField()
    congress = models.IntegerField()
    document_title = models.CharField(max_length=765)
    speaker_raw = models.CharField(max_length=765)
    speaker_firstname = models.CharField(max_length=765)
    speaker_lastname = models.CharField(max_length=765)
    speaker_state = models.CharField(max_length=6)
    speaker_bioguide = models.CharField(max_length=21)
    speaker_party = models.CharField(max_length=9)
    ngram = models.CharField(max_length=765)
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams'

class UnigramsByCount(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count'

class UnigramsByCountBioguide(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__bioguide'

class UnigramsByCountBioguideCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__bioguide_congress'

class UnigramsByCountBioguideDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    bioguide = models.CharField(max_length=21)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__bioguide_date'

class UnigramsByCountBioguideYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    bioguide = models.CharField(max_length=21)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__bioguide_year'

class UnigramsByCountChamber(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber'

class UnigramsByCountChamberCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(max_length=765)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_congress'

class UnigramsByCountChamberCongressParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_congress_party'

class UnigramsByCountChamberCongressPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_congress_party_state'

class UnigramsByCountChamberDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_date'

class UnigramsByCountChamberDateParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_date_party'

class UnigramsByCountChamberDatePartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_date_party_state'

class UnigramsByCountChamberParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_party'

class UnigramsByCountChamberPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_party_state'

class UnigramsByCountChamberPartyStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_party_state_year'

class UnigramsByCountChamberPartyYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_party_year'

class UnigramsByCountChamberState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    chamber = models.CharField(max_length=3)
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_state'

class UnigramsByCountChamberYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    chamber = models.CharField(max_length=3)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__chamber_year'

class UnigramsByCountCongress(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__congress'

class UnigramsByCountCongressParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__congress_party'

class UnigramsByCountCongressPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__congress_party_state'

class UnigramsByCountCongressState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    congress = models.IntegerField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__congress_state'

class UnigramsByCountDate(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__date'

class UnigramsByCountDateParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__date_party'

class UnigramsByCountDatePartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__date_party_state'

class UnigramsByCountDateState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    date = models.DateField()
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__date_state'

class UnigramsByCountParty(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__party'

class UnigramsByCountPartyState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__party_state'

class UnigramsByCountPartyStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    state = models.CharField(max_length=6)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__party_state_year'

class UnigramsByCountPartyYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    party = models.CharField(max_length=9)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__party_year'

class UnigramsByCountState(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__state'

class UnigramsByCountStateYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    state = models.CharField(max_length=6)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__state_year'

class UnigramsByCountYear(models.Model):
    id = models.IntegerField(primary_key=True)
    ngram = models.CharField(unique=True, max_length=765)
    year = models.TextField() # This field type is a guess.
    count = models.IntegerField()
    class Meta:
        db_table = u'unigrams_by_count__year'

'''
