import time
from datetime import datetime
from contextlib import contextmanager

from django.test import TestCase
from django.test import override_settings
from django.test import Client
from django.conf import settings

from elasticsearch_dsl import Search, Index, DocType, Date, Text
from elasticsearch_dsl.connections import connections
from freezegun import freeze_time

from cwapi.es_docs import CRECDoc, get_term_count_in_doc, get_term_count_agg
from cwapi.views import search_text_match


class CountTermsTestCase(TestCase):

    def setUp(self):
        self.es_conn = connections.get_connection()
        self.test_crecs = []
        for i in range(20):
            self.test_crecs.append(
                CRECDoc(
                    title=str(i),
                    content='foo bar baz Foo',
                    date_issued=datetime(2017, 1, i % 5 + 1)
                )
            )
        self.index = Index(settings.ES_CW_INDEX)
        CRECDoc.init()
        for c in self.test_crecs:
            c.save(refresh=True)
        self.client = Client()

    def tearDown(self):
        self.index.delete()

    def test_num_docs_found(self):
        start_date = datetime(2017, 1, 1)
        end_date = datetime(2017, 1, 1)
        results = get_term_count_in_doc(
            self.es_conn, 'foo', start_date, end_date
        )
        buckets = get_term_count_agg(results)
        self.assertIsNotNone(buckets)
        self.assertEquals(len(buckets), 1)
        count = buckets[0].get('term_counts', {}).get('value')
        self.assertEquals(count, 8)

    def test_bucketing(self):
        start_date = datetime(2017, 1, 1)
        end_date = datetime(2017, 1, 30)
        results = get_term_count_in_doc(
            self.es_conn, 'foo', start_date, end_date
        )
        buckets = get_term_count_agg(results)
        self.assertIsNotNone(buckets)
        self.assertEquals(len(buckets), 5)
        for b in buckets:
            count = b.get('term_counts', {}).get('value')
            self.assertEquals(count, 8)

    def test_case_sensitivity(self):
        start_date = datetime(2017, 1, 1)
        end_date = datetime(2017, 1, 1)
        results = get_term_count_in_doc(
            self.es_conn, 'FOO', start_date, end_date
        )
        buckets = get_term_count_agg(results)
        self.assertIsNotNone(buckets)
        self.assertEquals(len(buckets), 1)
        count = buckets[0].get('term_counts', {}).get('value')
        self.assertEquals(count, 8)

    def test_api_start_end_specified(self):
        start_date = datetime(2017, 1, 1)
        end_date = datetime(2017, 1, 31)
        query_args = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'term': 'foo',
        }
        response = self.client.get('/cwapi/term_counts_by_day/', query_args)
        self.assertEquals(200, response.status_code)
        response_content = response.json()
        self.assertEqual('success', response_content['status'])
        self.assertEquals(31, len(response_content['data']['daily_counts']))
        total = 0
        for date_str, count in response_content['data']['daily_counts'].items():
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            self.assertTrue(dt >= start_date and dt <= end_date)
            if dt.day > 5:
                self.assertEquals(0, count)
            else:
                self.assertEquals(8, count)
            total += count
        self.assertEquals(40, total)

    @freeze_time('2017-01-31')
    def test_api_days_ago(self):
        query_args = {
            'days_ago': 30,
            'term': 'foo',
        }
        response = self.client.get('/cwapi/term_counts_by_day/', query_args)
        self.assertEquals(200, response.status_code)
        response_content = response.json()
        self.assertEqual('success', response_content['status'])
        self.assertEquals(31, len(response_content['data']['daily_counts']))
        for date_str in response_content['data']['daily_counts'].keys():
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            self.assertTrue(
                dt >= datetime(2017, 1, 1) and dt <= datetime(2017, 1, 31)
            )


class SearchByFieldTestCase(TestCase):

    def setUp(self):
        self.es_conn = connections.get_connection()
        self.test_crecs = []
        for i in range(20):
            self.test_crecs.append(
                CRECDoc(
                    title=str(i),
                    content='foo bar baz Foo',
                    date_issued=datetime(2017, 1, i % 5 + 1)
                )
            )
        self.index = Index(settings.ES_CW_INDEX)
        CRECDoc.init()
        for c in self.test_crecs:
            c.save(refresh=True)
        self.client = Client()

    def tearDown(self):
        self.index.delete()
    
    def test_search_by_title(self):
        c = CRECDoc(
            title='foo',
            content='blah',
            date_issued=datetime(2017, 1, 1)
        )
        c.save(refresh=True)
        start_date = datetime(2017, 1, 1)
        end_date = datetime(2017, 1, 30)
        query_args = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'title': 'foo',
        }
        response = self.client.get('/cwapi/search/', query_args)
        response_content = response.json()
        results = response_content['data']
        self.assertEquals(1, len(results))
        self.assertEquals('foo', results[0]['title'])
        self.assertEquals('blah', results[0]['content'])
    
    def test_search_by_content(self):
        c = CRECDoc(
            title='foo',
            content='blah',
            date_issued=datetime(2017, 1, 1)
        )
        c.save(refresh=True)
        start_date = datetime(2017, 1, 1)
        end_date = datetime(2017, 1, 30)
        query_args = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'content': 'blah',
        }
        response = self.client.get('/cwapi/search/', query_args)
        response_content = response.json()
        results = response_content['data']
        self.assertEquals(1, len(results))
        self.assertEquals('foo', results[0]['title'])
        self.assertEquals('blah', results[0]['content'])
    
        
    def test_date_filter(self):
        c = CRECDoc(
            title='should be in results',
            content='blah',
            date_issued=datetime(2017, 1, 1)
        )
        c2 = CRECDoc(
            title='should NOT be in results',
            content='blah',
            date_issued=datetime(2016, 1, 1)
        )
        c.save(refresh=True)
        c2.save(refresh=True)
        start_date = datetime(2017, 1, 1)
        end_date = datetime(2017, 1, 30)
        query_args = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'content': 'blah',
        }
        response = self.client.get('/cwapi/search/', query_args)
        response_content = response.json()
        results = response_content['data']
        self.assertEquals(1, len(results))
        self.assertEquals('should be in results', results[0]['title'])
    
            
    def test_multi_field(self):
        c = CRECDoc(
            title='foo',
            content='bar',
            date_issued=datetime(2017, 1, 1)
        )
        c2 = CRECDoc(
            title='foo',
            content='baz',
            date_issued=datetime(2016, 1, 1)
        )
        c.save(refresh=True)
        c2.save(refresh=True)
        start_date = datetime(2017, 1, 1)
        end_date = datetime(2017, 1, 30)
        query_args = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'content': 'bar',
            'title': 'foo',
        }
        response = self.client.get('/cwapi/search/', query_args)
        response_content = response.json()
        results = response_content['data']
        self.assertEquals(1, len(results))
    
    
    def test_pagination(self):
        start_date = datetime(2017, 1, 1)
        end_date = datetime(2017, 1, 30)
        query_args = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'content': 'foo',
        }
        response = self.client.get('/cwapi/search/', query_args)
        response_content = response.json()
        max_score1 = max([d['score'] for d in response_content['data']])
        self.assertIsNotNone(max_score1)
        self.assertEquals(10, len(response_content['data']))
        query_args['offset'] = 10
        response = self.client.get('/cwapi/search/', query_args)
        response_content = response.json()
        max_score2 = max([d['score'] for d in response_content['data']])
        self.assertIsNotNone(max_score2)
        self.assertTrue(max_score1 >= max_score2)
        self.assertEquals(10, len(response_content['data']))
    