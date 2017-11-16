import logging
from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from scraper.models import CRECScraperResult
from scraper.crec_scraper import CRECScraper


class Command(BaseCommand):
    help = 'Scrapes CREC from gpo.gov for the given date range and stores in s3.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            help='If true, will not upload to es and instead print to stdout.',
            default=False,
        )
        parser.add_argument(
            '--start_date',
            help='Start of date range to pull data for, inclusive.',
            type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
        )
        parser.add_argument(
            '--end_date',
            help='End of date range to pull data for, exclusive.',
            type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
            default=None,
        )
        parser.add_argument(
            '--s3_bucket',
            help='Location of crec data.',
            default=settings.CREC_STAGING_S3_BUCKET
        )

    def handle(self, *args, **options):
        start_date = options['start_date']
        if options['end_date'] is None:
            end_date = datetime.utcnow()
        else:
            end_date = options['end_date']
        start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        scraper = CRECScraper(options['s3_bucket'])
        while start_date < end_date:
            result = scraper.scrape_files_for_date(start_date)
            start_date += timedelta(days=1)
