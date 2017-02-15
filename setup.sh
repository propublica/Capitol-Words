#!/usr/bin/env bash
#
# source me


# The filesystem path to the Capitol Words source directory.
export CAPWORDS_HOME="/cwod"

# The location of a Python virtual environment to run Capitol Words. Should contain a `bin/activate` script.
export CAPWORDS_VENV="/home/vagrant/.virtualenvs/capitolwords"

# The filesystem path to a temporary directory Capitol Words can safely make use of.
export CAPWORDS_TMP="/tmp/capwords/"

# The filesystem path to a log directory.
export CAPWORDS_LOGS="/tmp/logs/"

# The domain name used for this copy of Capitol Words. No trailing slash. Examples might be `http://localhost:8000` for a local install and `http://dev.capitolwords.org` for a shared development site.
export CAPWORDS_BASEURL="http://localhost:8000"

# The API key for the Sunlight Foundation APIs. (Use of this is not well-understood right now, and the existing Sunlight APIs don't require a key for the time being.)
export CAPWORDS_SUNLIGHT_APIKEY=""

# The URL to a running Solr service. Examples might be `localhost:8983/solr` for a local installation or `internal.solr:8983/capwords-core` for a Solr Cloud service running in a Kubernetes cluster which has multiple collections.IKEY
export CAPWORDS_SOLR_URL="localhost:8983/solr"

# Optional. Replaces the creation of a local_settings.py file with a `DATABASES = ` object. This variable should be a base64-encoded JSON object which decodes to the contents of the `DATABASES` settings object.
# export CAPWORDS_DATABASE=""

mkdir -p $CAPWORDS_TMP
mkdir -p $CAPWORDS_LOGS