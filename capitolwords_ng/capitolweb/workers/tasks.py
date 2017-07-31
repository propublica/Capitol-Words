from datetime import datetime
from datetime import timedelta

from celery import shared_task

from django.conf import settings
from workers.crec_scraper import CRECScraper
from workers.models import CRECScraperResult


def parse_and_floor_date_str(date_str):
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    else:
        date = datetime.utcnow() - timedelta(days=2)
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


@shared_task
def scrape_crecs(start_dt_str=None, end_dt_str=None):
    start_dt = parse_and_floor_date_str(start_dt_str)
    end_dt = parse_and_floor_date_str(end_dt_str)
    scraper = CRECScraper(
        settings.CREC_STAGING_FOLDER,
        settings.CREC_STAGING_S3_BUCKET,
        settings.CREC_STAGING_S3_KEY_PREFIX,
    )
    results = []
    while start_dt < end_dt:
        result = scraper.scrape_files_for_date(start_dt)
        results.append(result)
        orm_result = CRECScraperResult.objects.create(
            date=result['date'],
            message=result['message'],
            success=result['success'],
            num_crec_files_uploaded=result['num_crec_files_uploaded'],
        )
        start_dt += timedelta(days=1)
    return results

@shared_task
def parse_crecs(start_dt_str=None, end_dt_str=None):