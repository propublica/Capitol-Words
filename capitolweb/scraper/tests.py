import os
from datetime import datetime

import requests_mock
import requests
import boto3
from lxml import etree
from moto import mock_s3
from django.test import TestCase
from django.test import override_settings
from django.conf import settings

from scraper.crec_scraper import CRECScraper

@mock_s3
@requests_mock.Mocker()
@override_settings(
    CREC_STAGING_S3_BUCKET='my-test-bukkit',
    CREC_STAGING_S3_ROOT_PREFIX='crec-test',
)
class CRECScraperTestCase(TestCase):
    
    def setUp(self):
        self.s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        self.s3_bucket = self.s3.Bucket(settings.CREC_STAGING_S3_BUCKET)
        self.s3_bucket.create()
        self.crec_scraper = CRECScraper(s3_bucket=settings.CREC_STAGING_S3_BUCKET)
        self.test_date = datetime(2017, 1, 20)
        with open('scraper/test_resources/CREC-2017-01-20.zip', 'rb') as f:
            self.test_zip_data = f.read()
    
    def test_download_crec_zip(self, requests_mocker):
        requests_mocker.register_uri(
            'GET',
            'https://www.gpo.gov/fdsys/pkg/CREC-2017-01-20.zip',
            content=self.test_zip_data
        )
        crec_url = self.crec_scraper.get_crec_zip_url(self.test_date)
        self.assertTrue(crec_url)
        crec_zip = self.crec_scraper.download_crec_zip(crec_url)
        self.assertTrue(crec_zip)
        self.assertTrue(len(crec_zip.filelist) > 0)
        html_files = [
            f for f in crec_zip.filelist
            if f.filename.endswith('.htm')
        ]
        mods_files = [
            f for f in crec_zip.filelist
            if f.filename.endswith('mods.xml')
        ]
        self.assertTrue(len(html_files) > 0)
        self.assertTrue(len(mods_files) == 1)
        with crec_zip.open(mods_files[0]) as f:
            doc = etree.parse(f)
            self.assertTrue(doc.getroot().get('ID'))
    
    def test_upload_to_s3(self, requests_mocker):        
        requests_mocker.register_uri(
            'GET',
            'https://www.gpo.gov/fdsys/pkg/CREC-2017-01-20.zip',
            content=self.test_zip_data
        )
        crec_url = self.crec_scraper.get_crec_zip_url(self.test_date)
        zf = self.crec_scraper.download_crec_zip(crec_url)
        s3_keys = self.crec_scraper.extract_and_upload_to_s3(zf, self.test_date)
        crec_filenames = [
            f.filename for f in zf.filelist
            if f.filename.endswith('.htm')
        ]
        self.assertEquals(len(s3_keys), len(crec_filenames) + 1)
        for s3_key in s3_keys:
            obj = self.s3.Object(settings.CREC_STAGING_S3_BUCKET, s3_key)
            response = obj.get()
            self.assertTrue(response)
            if s3_key.endswith('mods.xml'):
                doc = etree.parse(response['Body'])
                self.assertTrue(doc.getroot().get('ID'))
    
    def test_scrape_files_for_date(self, requests_mocker):
        requests_mocker.register_uri(
            'GET',
            'https://www.gpo.gov/fdsys/pkg/CREC-2017-01-20.zip',
            content=self.test_zip_data
        )
        result = self.crec_scraper.scrape_files_for_date(self.test_date)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
