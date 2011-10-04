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

