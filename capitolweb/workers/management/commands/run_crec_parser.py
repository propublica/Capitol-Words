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

from workers.crec_parser import CRECParser


MODS_KEY_TEMPLATE = 'crec/%Y/%m/%d/mods/mods.xml'


class Command(BaseCommand):
    help = 'Runs the CREC parser.'

    def add_arguments(self, parser):
        output_option_group = parser.add_mutually_exclusive_group(required=True)
        output_option_group.add_argument(
            '--to_stdout',
            help='If true, will not upload to es and instead print to stdout.',
            default=False,
        )
        output_option_group.add_argument(
            '--es_url',
            help='Elastic search URL to upload records to.',
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
            default='capitol-words-data',
        )

    def handle(self, *args, **options):
        crec_parser = CRECParser(bucket=options['source_bucket'])

        s3 = boto3.resource('s3')
        dt = options['start_date'].replace(hour=0, minute=0, second=0, microsecond=0)
        if options['es_url']:
            parsed_es_url = urlparse.urlparse(options['es_url'])
            es_host = parsed_es_url.netloc
            index = parsed_es_url.path.strip('/')
            es_conn = elasticsearch.Elasticsearch([es_host])
        
        while dt < options['end_date']:
            logging.info('Processing files for {0}.'.format(dt))
            try:
                response = s3.Object(
                    options['source_bucket'],
                    dt.strftime(MODS_KEY_TEMPLATE)
                ).get()
            except botocore.exceptions.ClientError as e:
                logging.info('Could not find mods file for {0}.'.format(dt))
                response = None
            if response is not None and response.get('Body'):
                try:
                    input_stream = response['Body']
                    new_records = crec_parser.parse_mods_file(input_stream)
                    logging.info('Found {0} new records.'.format(len(new_records)))
                    if options['to_stdout']:
                        logging.info('Using stdout:')
                        for r in new_records:
                            logging.info(r)
                    else:
                        for r in new_records:
                            es_conn.index(index=index, doc_type='crec', id=r['ID'], body=r)
                except Exception as e:
                    logging.exception('Error processing data for {0}.'.format(dt.strftime('%Y-%m-%d')))
            dt += timedelta(days=1)
