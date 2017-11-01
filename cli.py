import sys
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


def setup_logger(loglevel):
    loglevel = LOGLEVELS.get(loglevel.upper())
    if loglevel is None:
        loglevel = LOGLEVELS['INFO']
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(loglevel)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def add_logging_options(parser):
    parser.add_argument(
        '--loglevel',
        help='Log level, one of INFO, ERROR, WARN, DEBUG or CRITICAL.',
        default='INFO',
    )
