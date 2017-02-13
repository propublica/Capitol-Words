Capitol Words is a Django project which uses a combination of regular scraping and Solr indices to compile a searachable database of the Congressional Record.

## Requirements
* A Python environment suitable for deploying a Django webapp
* Python packages listed in `cwod_site/requirements.txt`
* A MySQL service
* A Solr (v1.4 to 3.6 for now) service configured to use the provided schema.xml and stopwords.xml
* Eventually - SunlightLabs API key

Setup:
* For the sake of portability, most environment-specific configuration can be input via shell environment variables:
  * `CAPWORDS_HOME`: The filesystem path to the Capitol Words source directory.
  * `CAPWORDS_VENV`: The location of a Python virtual environment to run Capitol Words. Should contain a `bin/activate` script.
  * `CAPWORDS_TMP`: The filesystem path to a temporary directory Capitol Words can safely make use of.
  * `CAPWORDS_LOGS`: The filesystem path to a log directory.
  * `CAPWORDS_BASEURL`: The domain name used for this copy of Capitol Words. No trailing slash. Examples might be `http://localhost:8000` for a local install and `http://dev.capitolwords.org` for a shared development site.
  * `CAPWORDS_SUNLIGHT_APIKEY`: The API key for the Sunlight Foundation APIs. (Use of this is not well-understood right now, and the existing Sunlight APIs don't require a key for the time being.)
  * `CAPWORDS_SOLR_URL`: The URL to a running Solr service. Examples might be `localhost:8983/solr` for a local installation or `internal.solr:8983/capwords-core` for a Solr Cloud service running in a Kubernetes cluster which has multiple collections.
  * `CAPWORDS_DATABASE`: Optional. Replaces the creation of a local_settings.py file with a `DATABASES = ` object. This variable should be a base64-encoded JSON object which decodes to the contents of the `DATABASES` settings object.

* If no `CAPWORDS_DATABASE` environment variable is provided, create a `cwod_site/local_settings.py` file and add the proper database credentials there.
* Running copies of the site (not necessarily local environments) should install cronjobs based on the cron template provided in the `prod-crontab` file.

## Ongoing/working notes by Kaz

* I have replaced all hard-coded config options I can find with shell vars. It should be relatively simple for either a developer installing locally or someone setting up a Docker-powered version to supply these variables as part of their setup process.
* More remains to be done -- I don't understand the various remote APIs very well and there are still a few hard-coded URLs I have not yet fully replaced.
* We need to load the existing Solr data files into a Solr service at version 3.6 or earlier and make sure it still works. Once that's done, we can figure out how to upgrade over time while not losing that data.
* I omitted a test version of a Docker Compose file that I used to boot up services (since I don't have the data to test them anyway) but I would recommend `harisekhon/solr:3.6` for a Solr image and `mysql:5.5` for a database image. (I stuck with an old version of MySQL for "just in case" reasons.)

