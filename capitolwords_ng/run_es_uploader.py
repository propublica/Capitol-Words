from __future__ import print_function

import os
import json
import logging
import argparse
import urlparse
from datetime import datetime
from datetime import timedelta

import elasticsearch

from cli import setup_logger
from cli import add_logging_options
from cli import CMD_LINE_DATE_FORMAT
from parsers.crec import CRECParser


PARSERS = {
    'crec': CRECParser,
}


class OutputDestinationError(Exception):
    pass


def get_es_conn(es_host):
    parsed_url = urlparse.urlparse(es_url)
    es_host = parsed_url.netloc
    index = parsed_url.path.strip('/')
    if not es_host or not index:
        raise OutputDestinationError(
            'Could not extract host and index from {0}'.format(es_url)
        )
    logging.info('Connecting to Elasticsearch host "{0}" index "{1}".'.format(
        es_host, index
    ))
    return elasticsearch.Elasticsearch([es_host])


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
        '--source_path',
        help='Path to file to be parsed. Can be local disk or S3.'
    )
    parser.add_argument(
        '--data_type',
        help='Determines which parser to use.',
        choices=PARSERS.keys(),
    )
    args = parser.parse_args()

    if args.source_path.startswith('s3://'):
        s3 = boto3.client('s3')
        parsed_url = urlparse.urlparse(es_url)
        obj = s3.get_object(Bucket=parsed_url.netloc, Key=parsed_url.path)
        input_stream = obj['Body']
    else:
        input_stream = open(args.source_path)

    parser = PARSERS[args.data_type]()
    records = parser.parse_mods_file(input_stream)

    if args.to_stdout:
        for r in records:
            print(json.dumps(r))
    else:
        parsed_es_url = urlparse.urlparse(args.es_url)
        es_host = parsed_es_url.netloc
        index = parsed_es_url.path.strip('/')
        es_conn = elasticsearch.Elasticsearch([es_host])
        for r in records:
            es_conn.index(index=index, doc_type='crec', id=r['ID'], body=r)

    logging.debug('Extracted {0} records.'.format(len(records)))
