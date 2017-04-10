"""Service for staging unpacked html files from a daily zip of congressional
records retrieved from gpo.gov.

This module can be used either from the command line, or deployed as an AWS
Lambda function (see :func:``lambda_handler`` for details on lambda execution).

To run locally:

    ::

        python crec_stager.py --s3_bucket=mybukkit

Attributes:
    DEFAULT_LOG_FORMAT (:obj:`str`): A template string for log lines.
    LOGLEVELS (:obj:`dict`): A lookup of loglevel name to the loglevel code.
"""

from __future__ import print_function

import os
import sys
import urllib2
import logging
import argparse
from datetime import datetime
from datetime import timedelta
from zipfile import ZipFile
from collections import defaultdict

import boto3
import requests
from botocore.exceptions import ClientError

from constants import DEFAULT_LOG_FORMAT
from constants import LOGLEVELS
from constants import CMD_LINE_DATE_FORMAT


class CRECStager(object):
    """Downloads the zip for specified date from gpo.gov, unpacks all html files
    to disk, then uploads each one to S3.

    Args:
        date (:class:`datetime.datetime`): Date of records to download.
        download_dir (:obj:`str`): A directory to download and unpack the
            CREC zip.
        s3_bucket (:obj:`str`): The name of an S3 bucket to stage unpacked html
            files in.
        s3_key_prefix (:obj:`str`): The prefix is prepended to each html
            filename to create the S3 key to upload it to.

    Attributes:
        CREC_ZIP_TEMPLATE (:obj:`str`): The endpoint template for a CREC zip.
    """

    CREC_ZIP_TEMPLATE = 'https://www.gpo.gov/fdsys/pkg/CREC-%Y-%m-%d.zip'
    MODS_ZIP_TEMPLATE = 'https://www.gpo.gov/fdsys/pkg/CREC-%Y-%m-%d/mods.xml'

    def __init__(self, date, download_dir, s3_bucket, s3_key_prefix):
        self.date = date
        self.download_dir = download_dir
        self.s3_bucket = s3_bucket
        self.s3_key_prefix = s3_key_prefix
        self.s3 = boto3.client('s3')

    def download_crec_zip(self):
        """Downloads the CREC zip for this date.

        Returns:
            :obj:`str`: The path to the downloaded zip.
        """
        url = self.date.strftime(self.CREC_ZIP_TEMPLATE)
        logging.info('Downloading CREC zip from "{0}".'.format(url))
        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError as e:
            if e.getcode() == 404:
                logging.debug('No zip found for date {0}'.format(self.date))
                return None
        zip_path = os.path.join(self.download_dir, url.split('/')[-1])
        zip_data = response.read()
        with open(zip_path, 'wb') as f:
            f.write(zip_data)
        return zip_path

    def download_mods_xml(self):
        """Downloads the mods.xml metadata file for this date to download_dir.

        Returns:
            :obj:`str`: Path to the downloaded mods.xml file.
        """
        url = self.date.strftime(self.MODS_ZIP_TEMPLATE)
        logging.info('Downloading mods.xml from "{0}".'.format(url))
        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError as e:
            if e.getcode() == 404:
                logging.debug('No mods.xml found for date {0}, at "{1}"'.format(
                        self.date, url
                    )
                )
                return None
        data = response.read()
        mods_path = os.path.join(self.download_dir, 'mods.xml')
        with open(mods_path, 'w') as f:
            f.write(data)
        return mods_path

    def extract_html_files(self, zip_path):
        """Unpacks all html files in the zip at the provided path to the value
        set in the instance variable ``CRECStager.download_dir``.

        Args:
            zip_path (:obj:`str`): Path to the CREC zip file.

        Returns:
            :obj:`list` of :obj:`str`: A list of the unpacked html files.
        """
        zip_filename = os.path.splitext(os.path.basename(zip_path))[0]
        html_prefix = os.path.join(zip_filename, 'html')
        html_filenames = []
        with ZipFile(zip_path) as crec_zip:
            for f in crec_zip.filelist:
                if f.filename.startswith(html_prefix):
                    html_filenames.append(f.filename)
                    crec_zip.extract(f, self.download_dir)
        return [
            os.path.join(self.download_dir, fname)
            for fname in html_filenames
        ]

    def upload_to_s3(self, file_path, data_type):
        """Uploads the file at the provided path to s3. The s3 key is
        generated from the date, the original filename, and the s3_key_prefix.

        Args:
            file_path (:obj:`str`): Path to html file.
            data_type (:obj:`str`): One of "crec" or "mods", used in s3 key.

        Returns:
            :obj:`str`: The S3 key the file was uploaded to.
        """
        s3_key = os.path.join(
            self.s3_key_prefix,
            self.date.strftime('%Y/%m/%d'),
            data_type,
            os.path.basename(file_path),
        )
        with open(file_path) as f:
            logging.debug(
                'Uploading "{0}" to "s3://{1}/{2}".'.format(
                    file_path, self.s3_bucket, s3_key
                )
            )
            self.s3.put_object(
                Body=f, Bucket=self.s3_bucket, Key=s3_key
            )
        return s3_key

    def stage_files(self):
        """Main entry point to staging process. Downloads the CREC zip for this
        date, unpacks all HTML files to disk, downloads the mods.xml metadata
        file, and uploads that and the unpacked HTML files.

        Returns:
            :obj:`bool`: True if all uploads were successful, False otherwise.
        """
        zip_path = self.download_crec_zip()
        mods_path = self.download_mods_xml()
        if zip_path is None:
            logging.info('No zip found for date {0}'.format(self.date))
            return None
        if mods_path is None:
            logging.info('No mods.xml found for date {0}'.format(self.date))
            return None
        logging.info(
            'Extracting html files from zip to {0}'.format(self.download_dir)
        )
        html_file_paths = self.extract_html_files(zip_path)
        try:
            s3_key = self.upload_to_s3(mods_path, 'mods')
        except ClientError as e:
            logging.exception(
                'Error uploading file {0}, exiting'.format(mods_path, e)
            )
            return False
        logging.info('Uploading {0} html files...'.format(len(html_file_paths)))
        for file_path in html_file_paths:
            try:
                s3_key = self.upload_to_s3(file_path, 'crec')
            except ClientError as e:
                logging.exception(
                    'Error uploading file {0}, exiting'.format(file_path, e)
                )
                return False
        logging.info('Uploads finished.')
        return True


def lambda_handler(event, context):
    """Entry point for AWS Lambda execution.

    In addition to the arguments specified below, this function also gets some
    settings from the following environment variables (set through the AWS
    console):
        LOGLEVEL
            loglevel for logging to cloudwatch
        DOWNLOAD_DIR
            what directory to download and unpack CREC zips and the mods.xml
            file. Must be under ``/tmp`` when running in lambda as everything
            else is write protected.
        S3_TARGET_BUCKET
            what s3 bucket to upload unpacked html files to.
        DATE
            what day to look for crec data for.

    Args:
        event (:obj:`dict`): A dictionary containg data from event trigger.
        context (:obj:`dict`): Context settings for this lambda job.
    """
    logger = logging.getLogger()
    logger.setLevel(os.environ.get('LOGLEVEL', 'INFO'))
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    download_dir = os.environ.get('DOWNLOAD_DIR', '/tmp')
    # date_str = os.environ.get('DATE', None)
    date_str = event['date']
    if date_str is None:
        date = datetime.utcnow() - timedelta(days=1)
    else:
        date = datetime.strptime(date_str, '%Y-%m-%d')

    s3_bucket = os.environ.get('S3_TARGET_BUCKET')
    if not s3_bucket:
        raise Exception('No s3 bucket defined in $S3_TARGET_BUCKET.')
    s3_key_prefix = os.environ.get('S3_KEY_PREFIX', 'capitolwords/')
    crec_stager = CRECStager(
        date,
        download_dir,
        s3_bucket,
        s3_key_prefix
    )
    crec_stager.stage_files()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--date',
        help='Date to retrieve records for, format is YYYY-MM-DD.',
        type=lambda d: datetime.strptime(d, CMD_LINE_DATE_FORMAT),
    )
    parser.add_argument(
        '--s3_bucket',
        help='Bucket to upload html files to.',
        default='use-this-bucket-to-test-your-bullshit',
    )
    parser.add_argument(
        '--s3_key_prefix',
        help='Key prefix for the html files staged in S3.',
        default='capitolwords/',
    )
    parser.add_argument(
        '--download_dir',
        help='Directory to write the zip and extracted files to.',
        default='/tmp'
    )
    parser.add_argument(
        '--loglevel',
        help='Log level, one of INFO, ERROR, WARN, DEBUG or CRITICAL.',
        default='INFO',
    )
    args = parser.parse_args()
    loglevel = LOGLEVELS.get(args.loglevel.upper())
    if loglevel is None:
        loglevel = LOGLEVELS['INFO']
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(loglevel)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    if args.date:
        dt = args.date
    else:
        dt = datetime.utcnow() - timedelta(days=1)
    if not os.path.exists(args.download_dir):
        os.makedirs(args.download_dir)
    crec_stager = CRECStager(
        dt,
        args.download_dir,
        args.s3_bucket,
        args.s3_key_prefix
    )
    crec_stager.stage_files()
