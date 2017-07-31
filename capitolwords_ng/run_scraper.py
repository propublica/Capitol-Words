"""Service for staging unpacked html files from a daily zip of congressional
records retrieved from gpo.gov.

To run locally:

    ::

        python run_scraper.py --s3_bucket=mybukkit --data_type=crec

Attributes:
    SCRAPERS (dict): A dict mapping data type label to scraper class.
"""
from __future__ import print_function

import os
import logging
import argparse
from datetime import datetime
from datetime import timedelta

from cli import setup_logger
from cli import add_logging_options
from cli import CMD_LINE_DATE_FORMAT
from capitolweb.workers.crec_scraper import CRECScraper


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
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
        '--s3_bucket',
        help='Bucket to upload html files to.',
        default='use-this-bucket-to-test-your-bullshit',
    )
    parser.add_argument(
        '--s3_prefix',
        help='Key prefix for the files being staged in S3.',
        default='capitolwords/',
    )
    parser.add_argument(
        '--download_dir',
        help='Directory to write the zip and extracted files to.',
        default='/tmp'
    )
    add_logging_options(parser)
    args = parser.parse_args()
    setup_logger(args.loglevel)

    if not os.path.exists(args.download_dir):
        os.makedirs(args.download_dir)

    scraper = CRECScraper(
        args.download_dir,
        args.s3_bucket,
        args.s3_prefix
    )
    scraper.scrape_files_in_range(args.start_dt, args.end_dt)
