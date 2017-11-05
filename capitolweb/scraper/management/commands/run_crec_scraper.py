from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from scraper.tasks import scrape_crecs
from scraper.models import CRECScraperResult


class Command(BaseCommand):
    help = 'Scrapes CREC from gpo.gov for the given date range and stores in s3.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            help='If true, will not upload to es and instead print to stdout.',
            default=False,
        )
        parser.add_argument(
            '--staging_folder',
            default=settings.CREC_STAGING_FOLDER
        )
        parser.add_argument(
            '--start_date',
            help='Start of date range to pull data for, inclusive.',
            type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
            default=None,
        )
        parser.add_argument(
            '--end_date',
            help='End of date range to pull data for, exclusive.',
            type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
            default=None,
        )
        parser.add_argument(
            '--staging_bucket',
            help='Location of crec data.',
            default=settings.CREC_STAGING_S3_KEY_PREFIX
        )

    def handle(self, *args, **options):
        start_date = parse_and_floor_date_str(options['start_date'])
        end_date = parse_and_floor_date_str(options['end_date'])
        scraper = CRECScraper(
            options['staging_folder'], 
            options['staging_bucket'],
            options['s3_prefix']
        )
        results = []
        while start_date < end_date:
            result = scraper.scrape_files_for_date(start_date)
            results.append(result)
            orm_result = CRECScraperResult.objects.create(
                date=result['date'],
                message=result['message'],
                success=result['success'],
                num_crec_files_uploaded=result['num_crec_files_uploaded'],
            )
            start_date += timedelta(days=1)
        return results
