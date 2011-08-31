from django.db import models

from bioguide.models import LegislatorRole


class NgramDateCount(models.Model):
    """Storing the total number of ngrams per date
    allows us to show the percentage of a given ngram
    on a given date, mainly for graphing purposes.
    """
    n = models.IntegerField(db_index=True)
    date = models.DateField(db_index=True)
    count = models.IntegerField()

    class Meta:
        unique_together = (('n', 'date', ), )


class Bill(models.Model):
    slug = models.SlugField()
    bill = models.CharField(max_length=32)
    congress = models.IntegerField()
    bill_title = models.TextField()
    last_action = models.TextField()
    last_action_date = models.DateField()
    sponsor = models.ForeignKey(LegislatorRole, related_name='sponsor', null=True)
    cosponsors = models.ManyToManyField(LegislatorRole, related_name='cosponsors')
    summary = models.TextField()
    url = models.URLField(verify_exists=False)
    source = models.CharField(max_length=255)

    class Meta:
        unique_together = (('slug', 'congress', ), )

    def __unicode__(self):
        return self.bill_title



class CRDoc(models.Model):
    """Caching some basic data about each Congressional Record
    document.
    """
    slug = models.SlugField(db_index=True)
    page_id = models.CharField(max_length=24, db_index=True)
    document_title = models.CharField(max_length=255)
    congress = models.IntegerField(db_index=True)
    session = models.IntegerField(db_index=True)
    date = models.DateField(db_index=True)
    chamber = models.CharField(max_length=24)

    legislators = models.ManyToManyField(LegislatorRole)
    bills = models.ManyToManyField(Bill)

    similar_documents = models.ManyToManyField('self')

    class Meta:
        unique_together = (('page_id', 'congress', 'session', ), )

    def __unicode__(self):
        return self.document_title.title().replace("'S", "'s")


class RepresentativeSentence(models.Model):
    """Sentences representative of a given document.
    """
    crdoc = models.ForeignKey(CRDoc)
    sentence = models.TextField()

    def __unicode__(self):
        return self.sentence
