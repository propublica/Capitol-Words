from collections import defaultdict
from settings import *
import glob
import json
import os
import re
import unittest
import urllib
import urllib2

class TestSolrNumbers(unittest.TestCase):

    def setUp(self):
        self.limit = 100
        self.solrdoc_counts = defaultdict(list)
        self.cache_solrdoc_counts()
        self.fields = ['unigrams', 'bigrams', 'trigrams', 'quadgrams', 'pentagrams',]

    def do_solr_query(self, data, field):
        body = urllib.urlencode(data)
        url = 'http://localhost:8983/solr/select?%s' % body
        json_data = json.loads(urllib2.urlopen(url).read())
        results = json_data['facet_counts']['facet_fields'][field]
        return results

    def get_top_phrases(self, field):
        data = {'q': '*:*',
                'facet.field': field,
                'rows': 0,
                'facet.method': 'enumtermfreq',
                'facet': 'true',
                'facet.sort': 'count',
                'facet.limit': self.limit,
                'wt': 'json', }
        results = self.do_solr_query(data, field)
        return zip(results[::2], results[1::2])

    def get_total_date_count(self, phrase, field):
        data = {'q': '%s:"%s"' % (field, phrase),
                'facet.field': 'date',
                'rows': 0,
                'facet.method': 'enumtermfreq',
                'facet': 'true',
                'facet.sort': 'index',
                'facet.limit': '-1',
                'wt': 'json', }
        results = self.do_solr_query(data, 'date')
        return sum(results[1::2])

    def cache_solrdoc_counts(self):
        path = os.path.join(CWOD_HOME, 'solrdocs')
        regex = re.compile('<field name="(?P<field>(?:uni|bi|tri|quad|penta)grams)">(?P<value>.*?)</field>')
        for filepath in glob.glob(path + '/*'):
            for line in open(filepath, 'r'):
                m = regex.match(line.strip())
                if not m:
                    continue
                field, value = m.groups()
                self.solrdoc_counts[field].append(value)

    def get_solrdoc_count(self, phrase, field):
        return len([x for x in self.solrdoc_counts[field] if x == phrase])

    def ngram_number_test(self, n):
        """Test that the numbers for top n-gram queries
        match the numbers for all dates combined.
        """
        field = self.fields[n-1]
        for phrase, count in self.get_top_phrases(field):
            total_date_count = self.get_total_date_count(phrase, field)
            solrdoc_count = self.get_solrdoc_count(phrase, field)
            # Use a percentage for solrdoc phrase counts, because sometimes
            # documents get skipped.
            solrdoc_pct_of_total = solrdoc_count / float(total_date_count)
            yield {'phrase': phrase,
                   'top_count': count,
                   'date_count': total_date_count, 
                   'solrdoc_count': solrdoc_count,
                   'solrdoc_pct': solrdoc_pct_of_total,
                   }

    def top_bioguide_ids_for_phrase(self, phrase):
        field = self.fields[len(phrase.split())-1]
        data = {'q': '%s:"%s"' % (field, phrase),
                'facet.field': 'speaker_bioguide',
                'rows': 0,
                'facet.method': 'enumtermfreq',
                'facet': 'true',
                'facet.sort': 'count',
                'facet.limit': self.limit,
                'facet.mincount': 1,
                'wt': 'json', }
        results = self.do_solr_query(data, 'speaker_bioguide')
        return zip(results[::2], results[1::2])

    def check_bioguide_date_phrase_count(self, phrase, bioguide_id):
        field = self.fields[len(phrase.split())-1]
        data = {'q': '(speaker_bioguide:%s AND %s:"%s")' % (bioguide_id, field, phrase),
                'facet.field': 'date',
                'rows': 0,
                'facet.method': 'enumtermfreq',
                'facet': 'true',
                'facet.sort': 'index',
                'facet.limit': '-1',
                'facet.mincount': 1,
                'wt': 'json', }
        results = self.do_solr_query(data, 'date')
        return sum(results[1::2])

    def test_ngrams(self):
        for n in range(1,6):
            for result in self.ngram_number_test(n):
                self.assertEqual(result['top_count'],
                                 result['date_count'])
                if result['solrdoc_pct'] != 1:
                    print result
                    #self.fail("solrdoc_pct is less than .9 percent of the top count")

                for bioguide_id, count in self.top_bioguide_ids_for_phrase(result['phrase']):
                    total_date_count = self.check_bioguide_date_phrase_count(result['phrase'],
                                                                             bioguide_id)
                    self.assertEqual(count, total_date_count)


if __name__ == '__main__':
    unittest.main()
