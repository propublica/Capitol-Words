from django.db import models

class RecentEntry(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50)
    date = models.DateField()
    num_speakers = models.IntegerField()
    page_id = models.CharField(max_length=10)

    class Meta:
        ordering = ['-date', '-num_speakers', ]
        unique_together = (('slug', 'date', 'page_id', ), )

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('cwod_entry_detail', [self.date.strftime('%Y'),
                                      self.date.strftime('%m'),
                                      self.date.strftime('%d'),
                                      self.page_id,
                                      self.slug, ])

    @models.permalink
    def date_url(self):
        return ('cwod_date_detail', [self.date.strftime('%Y'),
                                     self.date.strftime('%m'),
                                     self.date.strftime('%d'), ])
