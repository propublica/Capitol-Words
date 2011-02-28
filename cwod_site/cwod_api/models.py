from django.db import models

# Create your models here.

class CongressionalRecordVolume(models.Model):
    congress = models.IntegerField(db_index=True)
    session = models.CharField(max_length=10, db_index=True)
    volume = models.IntegerField()


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
