from collections import defaultdict
import csv
import glob
import os
import re
import sys

from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):

        fields = ['granule', 'page_id', 'pages', 'date', 'number', 'volume', 'session', 'congress',
                    'document_title', 'speaker_raw', 'speaker_firstname', 'speaker_middlename', 'speaker_lastname',
                    'speaker_state', 'speaker_district', 'speaker_bioguide', 'speaker_party', 'ngram', 'count', ]

        writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter='\t')
        field = args[0]
        start = args[1]


        xml_fieldnames = ['congress', 'date', 'document_title', 'id', 'number', 
                          'page_id', 'pages', 'session', 'volume', 'speaker_raw',
                          'speaker_firstname', 'speaker_middlename', 'speaker_lastname', 'speaker_state',
                          'speaker_district', 'speaker_bioguide', 'speaker_party', ]


        subdirs = [x.strip() for x in os.popen('find %s -type d | sort' % start) if len(x.strip().strip('/').split('/')) >= 3]
        for subdir in subdirs:
            xmlfiles = glob.glob('%s/*.xml' % subdir)
            for xmlfile in xmlfiles:
                doc = open(xmlfile, 'r').read()

                ngrams = defaultdict(int)

                for ngram in re.findall(r'name="%s">(.*?)<' % field, doc):
                    ngrams[ngram] += 1

                congress = re.search(r'name="congress">(.*?)<', doc).groups()[0]
                date = re.search(r'name="date">(.*?)<', doc).groups()[0]
                row = {}
                for fieldname in xml_fieldnames:
                    m = re.search(r'name="%s">(.*?)<' % fieldname, doc)
                    if m:
                        row[fieldname] = m.groups()[0].decode('windows-1252').encode('utf-8')  #encode('utf-8', 'ignore')
                    else:
                        row[fieldname] = ''

                    if fieldname == 'speaker_district' and row[fieldname] == 'N/A':
                        row[fieldname] = ''

                row['date'] = dateparse(row['date']).date().strftime('%Y-%m-%d')
                row['granule'] = row['id'].split('.')[0]

                for ngram, count in ngrams.iteritems():
                    row.update({'ngram': ngram, 'count': count, })
                    row = dict([(k, v) for k, v in row.iteritems() if k in fields])
                    writer.writerow(row)
