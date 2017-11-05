import logging
from datetime import datetime
from datetime import timedelta
import urllib.parse as urlparse

import boto3
import botocore
import elasticsearch
from celery import shared_task

from django.conf import settings
from workers.crec_parser import CRECParser
from workers.models import CRECParserResult


MODS_KEY_TEMPLATE = 'crec/%Y/%m/%d/mods/mods.xml'


def parse_and_floor_date_str(date_str):
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    else:
        date = datetime.utcnow() - timedelta(days=2)
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


@shared_task
def parse_crecs(start_dt_str=None,
                end_dt_str=None,
                source_bucket=settings.CREC_STAGING_S3_BUCKET,
                es_url=settings.CREC_ELASTICSEARCH_URL):
    s3 = boto3.resource('s3')
    start_date = parse_and_floor_date_str(start_dt_str)
    end_date = parse_and_floor_date_str(end_dt_str)
    parsed_es_url = urlparse.urlparse(es_url)
    es_host = parsed_es_url.netloc
    index = parsed_es_url.path.strip('/')
    es_conn = elasticsearch.Elasticsearch([es_host])

    crec_parser = CRECParser(source_bucket,)

    while start_date < end_date:
        logging.info(
            'Processing files for {0}.'.format(start_date.strftime('%Y-%m-%d'))
        )
        try:
            s3_key = start_date.strftime(MODS_KEY_TEMPLATE)
            response = s3.Object(source_bucket, s3_key).get()
        except botocore.exceptions.ClientError as e:
            logging.info('Could not find mods file for {0}.'.format(start_date))
            response = None
        if response is not None and response.get('Body'):
            try:
                input_stream = response['Body']
                new_records = crec_parser.parse_mods_file(input_stream)
                logging.info('Uploading records.'.format(len(new_records)))
                for r in new_records:
                    es_conn.index(
                        index=index, doc_type='crec', id=r['ID'], body=r
                    )
                    orm_result = CRECParserResult.objects.create(
                        date=r['date_issued'],
                        crec_s3_key=r['s3_key'],
                        message=r['title'],
                        success=True
                    )
            except Exception as e:
                logging.exception(
                    'Error processing data for {0}.'.format(start_date.strftime('%Y-%m-%d'))
                )
        start_date += timedelta(days=1)

