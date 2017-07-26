from __future__ import print_function

import os
import json
import logging
import argparse
import urllib.parse as urlparse
from datetime import datetime
from datetime import timedelta

import elasticsearch
import boto3

from cli import setup_logger
from cli import add_logging_options
from cli import CMD_LINE_DATE_FORMAT
from parsers.crec import CRECParser


MODS_KEY_TEMPLATE = 'crec/%Y/%m/%d/mods/mods.xml'


if __name__ == '__main__':
    logging.basicConfig(level=20,)
    parser = argparse.ArgumentParser()
    add_logging_options(parser)
    output_option_group = parser.add_mutually_exclusive_group(required=True)
    output_option_group.add_argument(
        '--to_stdout',
        help='If true, will not upload to es and instead print to stdout.',
        default=True,
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
        default = 'capitol-words-data',
    )
    args = parser.parse_args()
    parser = CRECParser(bucket=args.source_bucket,)

    s3 = boto3.client('s3')
    dt = args.start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if args.es_url:
        parsed_es_url = urlparse.urlparse(args.es_url)
        es_host = parsed_es_url.netloc
        index = parsed_es_url.path.strip('/')
        es_conn = elasticsearch.Elasticsearch([es_host])
    while dt < args.end_dt:
        logging.info('Processing files for {0}.'.format(dt))
        try:
            response = s3.get_object(
                Bucket=args.source_bucket,
                Key=dt.strftime(MODS_KEY_TEMPLATE))
        except Exception as e:
            logging.info('Could not find mods file for {0}.'.format(dt))
            response = None
        if response is not None and response.get('Body'):
            input_stream = response['Body']
            new_records = parser.parse_mods_file(input_stream)
            logging.info('Found {0} new records.'.format(len(new_records)))
            if args.to_stdout:
                logging.info('Using stdout:')
                for r in new_records:
                    logging.info(r)
            else:
                for r in new_records:
                    es_conn.index(index=index, doc_type='crec', id=r['ID'], body=r)

        dt += timedelta(days=1)
