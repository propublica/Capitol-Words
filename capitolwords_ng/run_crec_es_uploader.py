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
    parser = argparse.ArgumentParser()
    add_logging_options(parser)
    output_option_group = parser.add_mutually_exclusive_group(required=True)
    output_option_group.add_argument(
        '--to_stdout',
        help='If true, will not upload to es and instead print to stdout.',
        action='store_true'
    )
    output_option_group.add_argument(
        '--es_url',
        help='Elastic search URL to upload records to.',
    )
    parser.add_argument(
        '--file_path',
        help='Path to file to be parsed.'
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
    )
    args = parser.parse_args()

    parser = CRECParser(
        bucket=args.source_bucket,
    )
    records = []
    if args.file_path:
        input_stream = open(args.source_path)
        records = parser.parse_mods_file(input_stream)
    else:
        s3 = boto3.client('s3')
        dt = args.start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        while dt < args.end_dt:
            try:
                response = s3.get_object(
                    Bucket=args.source_bucket,
                    Key=dt.strftime(MODS_KEY_TEMPLATE)
                )
            except Exception as e:
                logging.info('Could not find mods file for {0}.'.format(dt))
                response = None
            if response is not None and response.get('Body'):
                input_stream = response['Body']
                records += parser.parse_mods_file(input_stream)
            dt += timedelta(days=1)
    if args.to_stdout:
        for r in records:
            print(r)
    else:
        parsed_es_url = urlparse.urlparse(args.es_url)
        es_host = parsed_es_url.netloc
        index = parsed_es_url.path.strip('/')
        es_conn = elasticsearch.Elasticsearch([es_host])
        for r in records:
            es_conn.index(index=index, doc_type='crec', id=r['ID'], body=r)
    logging.info('Extracted {0} records.'.format(len(records)))
