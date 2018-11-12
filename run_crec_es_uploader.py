from __future__ import print_function

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

from cli import setup_logger
from cli import add_logging_options
from cli import CMD_LINE_DATE_FORMAT
from capitolweb.workers.crec_parser import CRECParser


MODS_KEY_TEMPLATE = 'crec/%Y/%m/%d/mods/mods.xml'


if __name__ == '__main__':
    logging.basicConfig(level=20,)
    parser = argparse.ArgumentParser()
    add_logging_options(parser)
    output_option_group = parser.add_mutually_exclusive_group(required=True)
    output_option_group.add_argument(
        '--to_stdout',
        action='store_true',
        help='If true, will not upload to es and instead print to stdout.',
    )
    output_option_group.add_argument(
        '--es_url',
        help='Elastic search URL to upload records to.',
    )
    parser.add_argument(
        '--start_dt',
        help='Start of date range to pull data for, inclusive.',
        type=lambda d: datetime.strptime(d, CMD_LINE_DATE_FORMAT),
        default=None,
    )
    parser.add_argument(
        '--end_dt',
        help='End of date range to pull data for, exclusive.',
        type=lambda d: datetime.strptime(d, CMD_LINE_DATE_FORMAT),
        default=None,
    )
    parser.add_argument(
        '--source_bucket',
        help='Location of crec data.',
        default='capitol-words-data',
    )
    args = parser.parse_args()
    setup_logger(args.loglevel)
    crec_parser = CRECParser(bucket=args.source_bucket,)

    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    dt = args.start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if args.es_url:
        parsed_es_url = urlparse.urlparse(args.es_url)
        es_host = parsed_es_url.netloc
        index = parsed_es_url.path.strip('/')
        es_conn = elasticsearch.Elasticsearch([es_host])
    while dt < args.end_dt:
        logging.info('Processing files for {0}.'.format(dt))
        try:
            response = s3.Object(
                args.source_bucket,
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
                if args.to_stdout:
                    logging.info('Using stdout:')
                    for r in new_records:
                        logging.info(r)
                else:
                    for r in new_records:
                        es_conn.index(index=index, doc_type='crec', id=r['ID'], body=r)
            except Exception as e:
                logging.exception('Error processing data for {0}.'.format(dt.strftime('%Y-%m-%d')))
        dt += timedelta(days=1)
