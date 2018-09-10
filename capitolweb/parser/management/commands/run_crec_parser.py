import os
import sys
import json
import logging
import argparse
import urllib.parse as urlparse
from datetime import datetime
from datetime import timedelta

import elasticsearch
import botocore
import boto3
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from elasticsearch_dsl.connections import connections

from parser.crec_parser import extract_crecs_from_mods
from parser.crec_parser import upload_speaker_word_counts
from scraper.crec_scraper import crec_s3_key
from cwapi.es_docs import CRECDoc


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Runs the CREC parser.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to_stdout',
            help='If true, will not upload to es and instead print to stdout.',
            default=False,
        )
        parser.add_argument(
            '--es_url',
            help='Elastic search URL to upload records to.',
            default=settings.ES_URL,
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
            '--source_bucket',
            help='Location of crec data.',
            default=settings.CREC_STAGING_S3_BUCKET,
        )

    def handle(self, *args, **options):
        s3 = boto3.resource('s3')
        dt = options['start_date'].replace(hour=0, minute=0, second=0, microsecond=0)
        if not options['to_stdout']:
            connections.create_connection(hosts=[options['es_url']], **settings.ES_CONNECTION_PARAMS)
            CRECDoc.init()
        while dt < options['end_date']:
            logger.info('Processing files for {0}.'.format(dt))
            try:
                response = s3.Object(
                    options['source_bucket'],
                    crec_s3_key('mods.xml', dt)
                ).get()
            except botocore.exceptions.ClientError as e:
                logger.info('Could not find mods file for {0}.'.format(dt))
                response = None
            if response is not None and response.get('Body'):
                try:
                    crecs = extract_crecs_from_mods(response['Body'])
                    logger.info('Found {0} new records.'.format(len(crecs)))
                    if options['to_stdout']:
                        logger.info('Using stdout:')
                    for crec in crecs:
                        if not crec.is_skippable():
                            if options['to_stdout']:
                                logger.info(crec.to_es_doc())
                            else:
                                es_doc = crec.to_es_doc()
                                es_doc.save()
                            upload_speaker_word_counts(crec)
                except Exception as e:
                    logger.exception('Error processing data for {0}.'.format(dt.strftime('%Y-%m-%d')))
            dt += timedelta(days=1)
