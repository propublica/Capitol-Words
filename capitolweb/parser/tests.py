from datetime import datetime

from lxml import etree
from django.test import TestCase
from django.test import override_settings
from django.conf import settings

import requests_mock
import requests
import boto3
from moto import mock_s3

from cwapi.models import SpeakerWordCounts
from parser.crec_parser import CRECParser
from parser.crec_parser import extract_crecs_from_mods
from parser.crec_parser import upload_speaker_word_counts
from scraper.crec_scraper import CRECScraper


@mock_s3
@override_settings(
    CREC_STAGING_S3_BUCKET='my-test-bukkit',
    CREC_STAGING_S3_ROOT_PREFIX='crec-test',
)
class CRECParserTestCase(TestCase):
    
    @classmethod
    @mock_s3 # NOTE: This is required in addition to the class level decorator.
    def setUpTestData(cls):
        cls.xml_path = 'parser/test_resources/mods.xml'
        cls.s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        with open(cls.xml_path) as f:
            cls.crecs = extract_crecs_from_mods(f)
        cls.s3_bucket = cls.s3.Bucket(settings.CREC_STAGING_S3_BUCKET)
        cls.s3_bucket.create()
        cls.crec_scraper = CRECScraper(s3_bucket=settings.CREC_STAGING_S3_BUCKET)
        cls.test_date = datetime(2017, 1, 20)
        with open('scraper/test_resources/CREC-2017-01-20.zip', 'rb') as f:
            cls.test_zip_data = f.read()
        with requests_mock.Mocker() as m:
            m.get(
                'https://www.gpo.gov/fdsys/pkg/CREC-2017-01-20.zip',
                content=cls.test_zip_data
            )
            result = cls.crec_scraper.scrape_files_for_date(cls.test_date)
        s3 = boto3.client('s3')

    def test_id(self):
        for c in self.crecs:
            self.assertIsNotNone(c.id)
            self.assertTrue(len(c.id) > 0)

    def test_title(self):
        for c in self.crecs:
            self.assertIsNotNone(c.title)
            self.assertTrue(len(c.title) > 0)
        
    def test_title_part(self):
        for c in self.crecs:
            self.assertIsNotNone(c.title_part)
            self.assertTrue(len(c.title_part) > 0)
    
    def test_pdf_url(self):
        for c in self.crecs:
            self.assertIsNotNone(c.pdf_url)
            self.assertTrue(len(c.pdf_url) > 0)
    
    def test_html_url(self):
        for c in self.crecs:
            self.assertIsNotNone(c.html_url)
            self.assertTrue(len(c.html_url) > 0)

    def test_page_start(self):
        for c in self.crecs:
            self.assertIsNotNone(c.page_start)
            self.assertTrue(len(c.page_start) > 0)

    def test_page_end(self):
        for c in self.crecs:
            self.assertIsNotNone(c.page_end)
            self.assertTrue(len(c.page_end) > 0)

    def test_speakers(self):
        for c in self.crecs:            
            self.assertIsNotNone(c.speakers)
            for s in c.speakers:
                self.assertIsNotNone(s)
                self.assertTrue(len(s) > 0)

    def test_speaker_ids(self):
        for c in self.crecs:
            self.assertIsNotNone(c.speaker_ids)
            for name, bioguide_id in c.speaker_ids.items():
                self.assertIsNotNone(name)
                self.assertIsNotNone(bioguide_id)
                self.assertTrue(len(name) > 0)
                self.assertTrue(len(bioguide_id) > 0)
    
    def test_content(self):
        for c in self.crecs:
            self.assertIsNotNone(c.content)
            self.assertTrue(len(c.content) > 0)
    
    def test_named_entity_counts(self):
        for c in self.crecs:
            self.assertIsNotNone(c.content)
            self.assertTrue(len(c.content) > 0)
            self.assertTrue(type(c.named_entity_counts) == dict)
            for ne_type, freqs in c.named_entity_counts.items():
                self.assertTrue(len(freqs) > 0)
    
    def test_noun_chunks_counts(self):
        for c in self.crecs:
            self.assertIsNotNone(c.content)
            self.assertTrue(len(c.content) > 0)
            self.assertTrue(len(c.noun_chunks_counts) > 0)
            bools = []
            self.assertTrue(len(c.noun_chunks_counts) > 0)

    def test_segments(self):
        self.assertTrue(any([c.segments for c in self.crecs]))
        for c in self.crecs:
            if c.segments:
                self.assertTrue(len(c.segments[0]) > 0)
            
    def test_upload_speaker_word_counts(self):
        for c in self.crecs:
            upload_speaker_word_counts(c)
        sw_counts = SpeakerWordCounts.objects.all()
        crec_ids = {c.id for c in self.crecs}
        for sw_count in sw_counts:
            self.assertTrue(sw_count.crec_id in crec_ids)
