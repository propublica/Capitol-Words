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

from cli import setup_logger
from cli import add_logging_options
from cli import CMD_LINE_DATE_FORMAT


def get_dates(start_dt, end_dt=None):
    if end_dt is None:
        end_dt = datetime.utcnow()
    end_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if start_dt is None:
        start_dt = end_dt - timedelta(days=1)
    dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    dates = []
    while dt < end_dt:
        dates.append(dt)
        dt += timedelta(days=1)
    return dates


class CRECScraper(object):
    """Downloads the zip for specified date from gpo.gov, unpacks all html files
    to disk, then uploads each one to S3.

    Args:
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

    def __init__(self, download_dir, s3_bucket, s3_key_prefix):
        self.download_dir = download_dir
        self.s3_bucket = s3_bucket
        self.s3_key_prefix = s3_key_prefix
        self.s3 = boto3.client('s3')

    def download_crec_zip(self, date):
        """Downloads the CREC zip for this date.

        Returns:
            :obj:`str`: The path to the downloaded zip.
        """
        url = date.strftime(self.CREC_ZIP_TEMPLATE)
        logging.info('Downloading CREC zip from "{0}".'.format(url))
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            if e.getcode() == 404:
                logging.info('No zip found for date {0}'.format(date))
            else:
                logging.exception('Error retrieving CREC zip.')
            return None
        zip_path = os.path.join(self.download_dir, url.split('/')[-1])
        zip_data = response.read()
        with open(zip_path, 'wb') as f:
            f.write(zip_data)
        return zip_path

    def download_mods_xml(self, date):
        """Downloads the mods.xml metadata file for this date to download_dir.

        Returns:
            :obj:`str`: Path to the downloaded mods.xml file.
        """
        url = date.strftime(self.MODS_ZIP_TEMPLATE)
        logging.info('Downloading mods.xml from "{0}".'.format(url))
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            if e.getcode() == 404:
                logging.debug('No mods.xml found for date {0}, at "{1}"'.format(
                        date, url
                    )
                )
            else:
                logging.exception('Error retrieving mods.xml.')
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

    def upload_to_s3(self, file_path, data_type, date):
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
            date.strftime('%Y/%m/%d'),
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

    def scrape_files_for_date(self, date):
        zip_path = self.download_crec_zip(date)
        mods_path = self.download_mods_xml(date)
        if zip_path is None:
            logging.info('No zip found for date {0}'.format(date))
            return None
        if mods_path is None:
            logging.info('No mods.xml found for date {0}'.format(date))
            return None
        logging.info(
            'Extracting html files from zip to {0}'.format(self.download_dir)
        )
        html_file_paths = self.extract_html_files(zip_path)
        try:
            s3_key = self.upload_to_s3(mods_path, 'mods', date)
        except ClientError as e:
            logging.exception(
                'Error uploading file {0}, exiting'.format(mods_path, e)
            )
            return False
        logging.info('Uploading {0} html files...'.format(len(html_file_paths)))
        for file_path in html_file_paths:
            try:
                s3_key = self.upload_to_s3(file_path, 'crec', date)
            except ClientError as e:
                logging.exception(
                    'Error uploading file {0}, exiting'.format(file_path, e)
                )
                return False
        logging.info('Uploads finished.')
        return True

    def scrape_files_in_range(self, start_dt, end_dt):
        if end_dt is None:
            end_dt = datetime.utcnow()
        end_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        if start_dt is None:
            start_dt = end_dt - timedelta(days=1)
        dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        dates = []
        while dt < end_dt:
            self.scrape_files_for_date(dt)
            dt += timedelta(days=1)
