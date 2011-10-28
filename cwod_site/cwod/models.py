import datetime
import simplejson as json

from django.db import models
from django.core.urlresolvers import reverse

from baseconv import base62

import jsonfield

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

    CHART_COLOR_CHOICES = (
        (1, 'Light'),
        (2, 'Dark'),
    )

    CHART_TYPE_CHOICES = (
        (1, 'Overall'),
        (2, 'By Party'),
        (3, 'Double'),
    )

    img_src = models.TextField(blank=True, default='')
    overall_img_src = models.TextField(blank=True, default='')
    by_party_img_src = models.TextField(blank=True, default='')
    url = models.TextField()
    title = models.CharField(max_length=255)
    start_date = models.DateField(default='1996-01-01')
    end_date = models.DateField(default=datetime.date.today())
    chart_color = models.SmallIntegerField(max_length=255, choices=CHART_COLOR_CHOICES)
    chart_type = models.SmallIntegerField(max_length=255, choices=CHART_TYPE_CHOICES)
    extra = jsonfield.JSONField(blank=True, default='{}')

    def from_decimal(self):
        return base62.from_decimal(self.pk)

    def js_url(self):
        return '%s?c=%s' % (reverse('cwod_embed_js'), self.from_decimal())

