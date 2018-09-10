from elasticsearch.connection import RequestsHttpConnection
from requests_aws4auth import AWS4Auth

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'capitolwords',
        'USER': 'root',
        'PASSWORD': 'W1neMXlOEMTyD3SkUVmmH3YhGLV',
        'HOST': 'cr10t7ymou5smwq.cbqydh2evdro.us-east-1.rds.amazonaws.com',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

ALLOWED_HOSTS = ['ec2-18-204-248-183.compute-1.amazonaws.com','127.0.0.1']

CREC_STAGING_S3_BUCKET = 'pp-capitolwords'
CREC_STAGING_S3_ROOT_PREFIX = 'crec'
CREC_STAGING_FOLDER = '/tmp'

ES_URL = 'https://search-capword-elasti-1xmo4zbd8r3ad-a5gjwcyltzbyykiqpfkc57dzji.us-east-1.es.amazonaws.com'
ES_CONNECTION_PARAMS = {
    'use_ssl': True,
    'verify_certs': True,
    'timeout': 200,
    'http_auth': AWS4Auth(
        'AKIAISQ54FJR52TLBWZA',
        'Lk9wYrF/7S4HTpHiQsaYZ8+iYA82qUhQFVPRDAWk',
        'us-east-1',
        'es'
    ),
    'connection_class': RequestsHttpConnection
}
ES_CW_INDEX = 'capitol_words_crecs'

# You need a credentials file in addition to these values in settings
AWS_ACCESS_KEY = 'AKIAISQ54FJR52TLBWZA'
AWS_SECRET_ACCESS_KEY = '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'
