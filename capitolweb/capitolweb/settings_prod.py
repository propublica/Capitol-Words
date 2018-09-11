from elasticsearch.connection import RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'capitolwords',
        'USER': os.environ.get('CAPWORDS_DB_USER', ''),
        'PASSWORD': os.environ.get('CAPWORDS_DB_PASS', ''),
        'HOST': os.environ.get('CAPWORDS_DB_HOST', ''),
    }
}

ALLOWED_HOSTS = ['127.0.0.1']

ES_CW_INDEX = 'capitol_words_crecs'
CREC_STAGING_S3_BUCKET = 'pp-capitolwords'
CREC_STAGING_S3_ROOT_PREFIX = 'crec'
CREC_STAGING_FOLDER = '/tmp'
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

ES_URL = os.environ.get('CAPWORDS_ES_URL', '')
ES_CONNECTION_PARAMS = {
    'use_ssl': True,
    'verify_certs': True,
    'timeout': 200,
    'http_auth': AWS4Auth(
        os.environ.get('AWS_ACCESS_KEY', ''),
        os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
        'us-east-1',
        'es'
    ),
    'connection_class': RequestsHttpConnection
}
