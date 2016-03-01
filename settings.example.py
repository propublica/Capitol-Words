import os

# Sunlight Labs api key
API_KEY = "your sunlight api key"
CWOD_HOME = '/tmp/cr'
TMP_DIR = '/tmp/'
LOG_DIR = os.path.join(CWOD_HOME, 'log')

# how far back in time does the system check for congressional record
# documents? dd/mm/yyyy format.
OLDEST_DATE = '01/1/1994' # oldest date in system is around 1/25/1994
# where should the scraper log the files it's downloaded?
SCRAPER_LOG = os.path.join(LOG_DIR, 'scraper.log')
# what domain and port are solr listening on?
SOLR_DOMAIN = 'http://localhost:8983'

CWOD_HOME = "" # directory where data is downloaded, parsed, and ingested from
TMP_DIR = 'tmp/'
DB_PARAMS = ["localhost","username","password","capitolwords"]
DB_PATH = "" # path to api/capitolwords sqlite database
BIOGUIDE_LOOKUP_PATH = "" # path to api/bioguide_lookup.csv