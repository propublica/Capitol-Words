import json
import urllib2
import urllib
import datetime
import re
import sys
import time

from cwod_api.models import *

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import IntegrityError
from django.template.defaultfilters import slugify

import nltk
from summarize import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        already = RepresentativeSentence.objects.values_list('crdoc', flat=True).distinct()
        for doc in CRDoc.objects.all()[200:]:
            if doc.id in already:
                continue
            print doc.page_id
            url = 'http://capitolwords.org/api/text.json?%s' % urllib.urlencode(
                    {'congress': doc.congress,
                        'session': doc.session,
                        'page_id': doc.page_id, })
            data = json.loads(urllib2.urlopen(url).read())
            text = ''
            for result in data['results']:
                for graf in result.get('speaking') or []:
                    text += graf + ' '

            if not text:
                continue

            summary_sentences = create_summary(text)

            if summary_sentences:
                for sentence in summary_sentences:
                    s = RepresentativeSentence.objects.create(
                            crdoc=doc,
                            sentence=sentence)
                    print s
            print


def create_summary(text):
    text = re.sub(r'\s\s+', ' ', text)
    sentences = nltk.sent_tokenize(text)
    if len(sentences) < 10:
        num = 3
    else:
        num = 2

    summarizer = SimpleSummarizer()
    return nltk.sent_tokenize(summarizer.summarize(text, num))

