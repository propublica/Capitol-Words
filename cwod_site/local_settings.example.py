import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 		 # Add 'sqlite3', postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'capitolwords',                      # Or path to database file if using sqlite3.
        'USER': 'capitolwords',                      # Not used with sqlite3.
        'PASSWORD': 'capitolwords',                  # Not used with sqlite3.
        'HOST': 'localhost',                      	 # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      	     # Set to empty string for default. Not used with sqlite3.
    }
}

TEMPLATE_DIRS = (
	os.path.dirname(os.path.realpath(__file__)) + '/templates/'
)

NYT_API_KEY = ''

MEDIASYNC_AWS_KEY = ''
MEDIASYNC_AWS_SECRET = ''
MEDIASYNC_AWS_BUCKET = ''
MEDIASYNC_AWS_PREFIX = ''
MEDIASYNC_SERVE_REMOTE = False
MEDIA_VERSION = ''

SUNLIGHT_API_KEY = ""
API_ROOT = "capitolwords.org/api"

USE_LOCKSMITH = False
