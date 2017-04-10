import os

from django.conf import settings

# Sunlight Labs api key
API_KEY = os.environ.get("CAPWORDS_SUNLIGHT_APIKEY")
CWOD_HOME = os.environ.get("CAPWORDS_HOME")
TMP_DIR = os.environ.get("CAPWORDS_TMP")
LOG_DIR = os.environ.get("CAPWORDS_LOGS")

# how far back in time does the system check for congressional record
# documents? dd/mm/yyyy format.
OLDEST_DATE = '01/06/2010'

# where should the scraper log the files it's downloaded?
SCRAPER_LOG = os.path.join(LOG_DIR, 'scraper.log')

# what domain and port are solr listening on?
SOLR_DOMAIN = os.environ.get("CAPWORDS_SOLR_URL")

# Used in ingest.py when saving docs, not sure how it's used but I think it's just for debugging output.
SOLR_DOC_PATH = os.environ.get("SOLR_DOC_PATH")

# to initialize a sqllite3 connection to a table called cwod_congressionalrecordvolume
DB_PATH = "/dev/null"

'''
Some lawmakers are routinely referred to in a way that
means they won't be found using db_bioguide_lookup.  These
lawmakers should be placed in a pipe-delimited file
in BIOGUIDE_LOOKUP_PATH, e.g.:
J000126|eddie bernice johnson|2009|representative|texas
D000299|lincoln diaz-balart|2009|representative|florida
'''
BIOGUIDE_LOOKUP_PATH = "/dev/null"

'''
passed to MySQLdb.Connection(**DB_PARAMS) in solr lib for bioguide lookup stuff.
TODO: Replace MySQLdb.Connection with Django ORM
'''
DB_PARAMS = {
    'host': settings.DATABASES['default']['HOST'],
    'user': settings.DATABASES['default']['USER'],
    'passwd': settings.DATABASES['default']['PASSWORD'],
    'db': settings.DATABASES['default']['NAME'],
    'port': int(settings.DATABASES['default']['PORT']),
}

