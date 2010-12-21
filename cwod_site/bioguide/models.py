from django.db import models

class Legislator(models.Model):
    """Model representing a legislator in a session of congress.
    """
    bioguide_id = models.CharField(max_length=7, db_index=True)
    prefix = models.CharField(max_length=16)
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    suffix = models.CharField(max_length=16)
    birth_death = models.CharField(max_length=16)
    position = models.CharField(max_length=24)
    party = models.CharField(max_length=32)
    state = models.CharField(max_length=2)
    congress = models.CharField(max_length=3)

    class Meta:
        unique_together = (('bioguide_id', 'congress', 'position', ))

    def __unicode__(self):
        return ' '.join([self.prefix, self.first, self.last, self.suffix, ])
