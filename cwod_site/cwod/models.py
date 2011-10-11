from django.db import models

from baseconv import base62


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


class Embed(models.Model):
    img_src = models.TextField()
    url = models.TextField()
    title = models.CharField(max_length=255)
    chart_type = models.CharField(max_length=255)

    def from_decimal(self):
        return base62.from_decimal(self.pk)

    def js_url(self):
        return '%s?c=%s' % (reverse('cwod_embed_js'), self.from_decimal())
