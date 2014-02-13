import os

# Sunlight Labs api key
CURRENT_DIR = "/Path/To/Capitol-Words"
API_KEY = ""
CWOD_HOME = os.path.join(CURRENT_DIR, 'data/cr') # must be absolute path
TMP_DIR = 'tmp/'
LOG_DIR = os.path.join(CWOD_HOME, 'log')

# sqlite database
DB_PATH = "/Users/atul/Dropbox/Development/Capitol-Words/api/capitolwords.db"
# mysql Database
DB_PARAMS = ["localhost","username","password","capitolwords"]
# csv database
BIOGUIDE_LOOKUP_PATH = os.path.join(CURRENT_DIR, 'api/bioguide_lookup.csv')

# how far back in time does the system check for congressional record
# documents? dd/mm/yyyy format. 
# The first date ~ever~ should be around 1/25/1994 as of 2/15/2014.
OLDEST_DATE = '01/1/1994' 
# where should the scraper log the files it's downloaded?
SCRAPER_LOG = os.path.join(LOG_DIR, 'scraper.log')
# what domain and port are solr listening on?
SOLR_DOMAIN = 'http://localhost:8983'