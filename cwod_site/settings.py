# Django settings for api project.
import os
import sys

from django.core.urlresolvers import resolve

PROJECT_ROOT = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'cwod_site', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = '/media/'
ADMIN_MEDIA_PREFIX = os.path.join(PROJECT_ROOT, 'cwod_site', 'media')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'cwod_api.middleware.jsonp.JSONPMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'locksmith.auth.middleware.APIKeyMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

SESSIONS_ENGINE = 'django.contrib.sessions.backends.cookies'
SESSION_COOKIE_HTTPONLY = True

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

EMAIL_BACKEND = "postmark.backends.PostmarkBackend"
EMAIL_FROM = "contact@sunlightfoundation.com"

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'locksmith.hub.auth_backend.LocksmithBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'cwod.context_processors.recent_top_unigrams',
    'cwod.context_processors.search_terms',
    'cwod.context_processors.frontend_apikey',
)

INSTALLED_APPS = (
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.messages',
    'cwod',
    'cwod_api',
    'bioguide',
    'jsonfield',
    # 'locksmith.hub',
    'locksmith.auth',
    'locksmith.logparse',
    'gunicorn',
    'ngrams',
    'mediasync',
    'typogrify',
)

from local_settings import (MEDIASYNC_AWS_KEY, MEDIASYNC_AWS_SECRET,
                            MEDIASYNC_AWS_BUCKET, MEDIASYNC_AWS_PREFIX,
                            MEDIASYNC_SERVE_REMOTE, MEDIA_VERSION)

MEDIASYNC = {
    'BACKEND': 'mediasync.backends.s3',
    'AWS_KEY': MEDIASYNC_AWS_KEY,
    'AWS_SECRET': MEDIASYNC_AWS_SECRET,
    'AWS_BUCKET': MEDIASYNC_AWS_BUCKET,
    'AWS_PREFIX': MEDIASYNC_AWS_PREFIX,
    'MEDIA_URL': '/media/',
    'SERVE_REMOTE': MEDIASYNC_SERVE_REMOTE,
    'STATIC_ROOT': os.path.join(PROJECT_ROOT, 'cwod_site', 'media'),
    'PROCESSORS': (
            'mediasync.processors.slim.css_minifier',
            # 'mediasync.processors.closurecompiler.compile',
        ),
    'JOINED': {
            #'css/joined.css': ['css/main.css','css/jquery.ui/jquery.ui.all.css'],
            'js/joined.js': ['js/underscore/underscore-min.js',
                             'js/spin/spin.min.js',
                             'js/history/scripts/compressed/amplify.store.js',
                             'js/history/scripts/compressed/history.adapter.jquery.js',
                             'js/history/scripts/compressed/history.js',
                             'js/history/scripts/compressed/history.html4.js',
                             'js/jquery.ui/jquery.ui.core.js',
                             'js/jquery.ui/jquery.ui.widget.js',
                             'js/jquery.ui/jquery.ui.mouse.js',
                             'js/jquery.ui/jquery.ui.slider.js',
                             'js/jquery.imagesloaded.js',
                             'js/emphasis/emphasis.js',
                             'js/google-chart.js',
                             'js/capitolwords.js',
                             'js/annotations.js',
                             'js/app.js',],
            },

}

def api_resolve(x):
    match = resolve(x)
    if hasattr(match.func, 'handler'):
        # resolve piston resources
        return match.func.handler.__class__.__name__
    else:
        return match.func

LOCKSMITH_LOG_CUSTOM_TRANSFORM = api_resolve

try:
    from local_settings import *
except ImportError:
    sys.stderr.write("Unable to load local settings. Make sure local_settings.py exists and is free of errors.\n")
