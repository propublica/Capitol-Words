import os

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
