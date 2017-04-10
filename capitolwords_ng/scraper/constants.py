import logging


DEFAULT_LOG_FORMAT = ' '.join([
    '%(asctime)s',
    '%(levelname)s',
    'pid:%(process)d,',
    'file:%(filename)s:%(lineno)d>',
    '%(message)s',
])


LOGLEVELS = {
    'CRITICAL': logging.CRITICAL,
    'DEBUG': logging.DEBUG,
    'WARN': logging.WARN,
    'INFO': logging.INFO,
    'ERROR': logging.ERROR,
}


CMD_LINE_DATE_FORMAT = '%Y-%m-%d'


BILL_URL_TEMPLATE = 'https://www.gpo.gov/fdsys/browse/collection.action?collectionCode=BILLS&browsePath={n_congress}%2F{type}%2F%5B{interval}%5D&isCollapsed=false&leafLevelBrowse=false&isDocumentResults=true&ycord=406.3999938964844'


BILL_TYPES = {
    'hconres': 'House Concurrent Resolution',
    'hjres': 'House Joint Resolution',
    'hr': 'House Bill',
    'hres': 'House Resolution',
    'sconres': 'Senate Concurrent Resolution',
    'sjres': 'Senate Joint Resolution',
    's': 'Senate Bill',
    'sres': 'Senate Resolution',
}
