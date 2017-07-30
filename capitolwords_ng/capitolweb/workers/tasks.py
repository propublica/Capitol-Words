from datetime import datetime
from datetime import timedelta

from celery import shared_task

from django.conf import settings
from workers.crec import CRECScraper
from workers.models import CRECScraperResult


@shared_task
def scrape_crecs(start_dt_str=None, end_dt_str=None):
    if start_dt_str:
        start_dt = datetime.strptime(start_dt_str, '%Y-%m-%d')
    else:
        start_dt = datetime.utcnow() - timedelta(days=2)
    if end_dt_str:
        end_dt = datetime.strptime(end_dt_str, '%Y-%m-%d')
    else:
        end_dt = datetime.utcnow() - timedelta(days=1)
    start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
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
