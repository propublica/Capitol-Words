"""Stages unpacked html files in s3 from a daily zip of congressional records
retrieved from gpo.gov .
"""

import os
import io
import logging
from zipfile import ZipFile

import boto3
import requests
from botocore.exceptions import ClientError
from django.conf import settings

from scraper.models import CRECScraperResult


logger = logging.getLogger(__name__)


def crec_s3_key(filename, date_issued):
    """Location of a CREC document (or mods.xml file) within an S3 bucket.
    
    The key is comprised of a root prefix set in django settings, formatted
    date time and the filename, joined by "/".
    
    Args:
        filename (str): The name of the file, e.g. "mods.xml".
        date_issed (:class:`datetime.datetime`): The date issued as a datetime
            object.
    
    Returns:
        str: An s3 key where that file should be located.
    """
    return os.path.join(
        settings.CREC_STAGING_S3_ROOT_PREFIX,
        date_issued.strftime('%Y/%m/%d'),
        filename
    )


class CRECDataNotFoundException(Exception):
    """Indicates data for the given date cannot be found at the normal gpo.gov
    url."""
    
    def __init__(self, url):
        self.url = url


class CRECScraper(object):
    """Downloads the zip for specified date from gpo.gov and uploads all html
    and mods.xml files to s3.

    Args:
        s3_bucket (:obj:`str`): The name of an S3 bucket to stage unpacked html
            files in.

    Attributes:
        CREC_ZIP_TEMPLATE (:obj:`str`): The endpoint template for a CREC zip.
    """

    CREC_ZIP_URL_TEMPLATE = 'https://www.gpo.gov/fdsys/pkg/CREC-%Y-%m-%d.zip'

    def __init__(self, s3_bucket=settings.CREC_STAGING_S3_BUCKET):
        self.s3_bucket = s3_bucket
        self.s3 = boto3.resource('s3')

    def download_crec_zip(self, url):
        """Retrieves the CREC zip for this date from gpo.gov.

        Args:
            str: A gpo.gov URL to a CREC zip file.
            
        Raises:
            CRECDataNotFoundException: Indicates a 404 from gpo.gov, usually due
                to there being no data for the previous day (e.g. during a
                recess).

        Returns:
            :class:`zipfile.ZipFile`: An in-memory ZipFile object.
        """
        response = requests.get(url)
        if response.status_code == 404:
            raise CRECDataNotFoundException(url)
        if response.status_code != 200:
            raise Exception('Non-200 response code from gpo.gov for url "{0}"'.format(url))
        zf = ZipFile(io.BytesIO(response.content))
        return zf
    
    def is_relevant_filename(self, file_name):
        return file_name.endswith('htm') or file_name.endswith('mods.xml')
    
    def extract_and_upload_to_s3(self, crec_zip_file, date):
        """Uploads the file at the provided path to s3. See ``crec_scraper.crec_s3_key``
        for s3 key format.
    
        Args:
            file_path (str): Path to html file.
            date (:class:`datetime.datetime`): Date to upload data for.
        
        Returns:
            str: The S3 key the file was uploaded to.
        """
        s3_keys = []
        for zipped_file in crec_zip_file.filelist:
            if self.is_relevant_filename(zipped_file.filename):
                s3_key = crec_s3_key(os.path.basename(zipped_file.filename), date)
                s3_keys.append(s3_key)
                logger.debug(
                    'Uploading "{0}" to "s3://{1}/{2}".'.format(
                        zipped_file.filename, self.s3_bucket, s3_key
                    )
                )
                with crec_zip_file.open(zipped_file) as unzipped_file:
                    obj = self.s3.Object(self.s3_bucket, s3_key)
                    obj.upload_fileobj(unzipped_file)
        return s3_keys

    def get_crec_zip_url(self, date):
        """Returns the URL for the CREC zip file containing all CREC files for
        the given date.
        
        Args:
            date :obj:`datetime.datetime`: Date of CREC files.
        
        Returns:
            str: The URL to a CREC zip file at gpo.gov.
        """
        return date.strftime(self.CREC_ZIP_URL_TEMPLATE)

    def scrape_files_for_date(self, date):
        """Retrieve the zip file for the given date, unpack all CREC files and
        the mods.xml metadata file to memory, then upload to s3. Stores results
        in an ORM, ``scraper.models.CRECScraperResult``.
        
        Args:
            date (:class:`datetime.datetime`): The date to retreive docs for.
        
        Returns:
            :class:`scraper.models.CRECScraperResult`: An ORM model instance
                containing a summary of the scraper job results.
        """
        logger.info('Scraping data for {0}...'.format(date))
        orm_result = CRECScraperResult.objects.create(
            date=date,
            message='Job started.',
            success=False,
            num_crec_files_uploaded=0
        )
        url = date.strftime(self.CREC_ZIP_URL_TEMPLATE)
        try:
            crec_zip = self.download_crec_zip(self.get_crec_zip_url(date))
        except CRECDataNotFoundException as e:
            logger.info('No data found for date {0} at url "{1}"'.format(date, url))
            orm_result.success = True
            orm_result.save()
            return orm_result
        except Exception as e:
            orm_result.message = 'Error downloading CREC data for date {0} at url "{1}"'.format(date, url)
            logger.exception(orm_result.message)
            orm_result.save()
            return orm_result
        logger.info('Uploading extracted data to s3...')
        try:
            s3_keys = self.extract_and_upload_to_s3(crec_zip, date)
        except ClientError as e:
            orm_result.message = 'Error uploading CREC data to s3, exiting'
            logger.exception(orm_result.message)
            orm_result.save()
            return orm_result
        logger.info('Uploads finished.')
        orm_result.message = '\n'.join(s3_keys)
        orm_result.num_crec_files_uploaded = len(
            [k for k in s3_keys if k.endswith('.htm')]
        )
        orm_result.success = True
        orm_result.save()
        return orm_result
