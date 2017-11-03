from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from workers.tasks import scrape_crecs
from workers.models import CRECScraperResult


class Command(BaseCommand):
    help = 'Runs the CREC parser.'

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
            '--start_dt_str',
            help='Start of date range to pull data for, inclusive.',
            type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
            default=None,
        )
        parser.add_argument(
            '--end_dt_str',
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
        scrape_crecs(
            debug=options['debug'],
            staging_folder=options['debug'],
            start_dt_str=options['start_dt_str']
            end_dt_str=options['end_dt_str']
            staging_bucket=options['staging_bucket']
        )
        # 
        # start_dt_str=None,
        #              end_dt_str=None,
        #              debug=False,
        #              staging_folder=settings.CREC_STAGING_FOLDER,
        #              staging_bucket=settings.CREC_STAGING_S3_BUCKET,
        #              s3_prefix=settings.CREC_STAGING_S3_KEY_PREFIX):
    
    # 
    # start_dt = parse_and_floor_date_str(start_dt_str)
    # end_dt = parse_and_floor_date_str(end_dt_str)
    # scraper = CRECScraper(staging_folder, staging_bucket, s3_prefix)
    # results = []
    # while start_dt < end_dt:
    #     result = scraper.scrape_files_for_date(start_dt)
    #     results.append(result)
    #     orm_result = CRECScraperResult.objects.create(
    #         date=result['date'],
    #         message=result['message'],
    #         success=result['success'],
    #         num_crec_files_uploaded=result['num_crec_files_uploaded'],
    #     )
    #     start_dt += timedelta(days=1)
    # return results
