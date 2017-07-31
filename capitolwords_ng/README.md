# Capitol Words NG - The Upgrade

This will ultimately replace the top level codebase. Developed by [Chartbeat](https://www.chartbeat.com) Engineers during hackweeks!


## The API

The API is built on Django and it's broken into 2 apps:

    * cwapi - document search with elastic search
    * legislators - database of congress people


### Setup

To set up the API do the following:

    cd Capitol-Words/capitolwords_ng/capitolweb
    python manage.py migrate
    python manage.py loadcongress
    python manage.py createsuperuser (if you want to use the admin tool to browse)
    python manage.py runserver


### cwapi

The seach API is backed by elastic search and uses [elasticsearch-dsl-py](https://github.com/elastic/elasticsearch-dsl-py)

Endpoints:

    /cwapi/search/speaker/<name>
    /cwapi/search/title/<title>
    /cwapi/search/multi?<params>

`speaker` and `title` take a term match like: `/cwapi/search/speaker/Sanders`

The `multi` endpoint allows for full text search of documents combined with titles or speakers.

    title - search on the title field
    speaker - individual speakers
    content - search for text matches in the content add &highlight=<number> to include contextual
              matches of the given fragment size in the result (default is 200)

    Example:
        http://127.0.0.1:8000/cwapi/search/multi/?speaker=schumer&content=trump&highlight=1000

Currently all of these endpoints return an elastic search document as json.

### legislators api

The legislators are pulled from the [unitedstates/congress-legislators](https://github.com/unitedstates/congress-legislators) project and stored in the database.

Endpoints:

    /legislators/search
    /legislators/person/<bioguide_id>
    /legislators/current?state=<state 2 letter code>

 `person` allows lookup by the bioguide id
 `current` returns all of the current legislators with an optional 2 letter state code
 `search` allows for more complex queries:

        Search by query params
        supports the following ?term=val
        - id - the db id
        - name - matches against the official_full
        - last_name - last_name
        - gender
        - religion

        additionally supports boolean current to match only current reps

        example:
            http://127.0.0.1:8000/legislators/search/?gender=F&religion=Jewish
            http://127.0.0.1:8000/legislators/search/?gender=F&religion=Jewish&current


The record returned includes Term objects for every term served by the Congress Person along with bio data and ids to other databases and services.

## Frontend (single-page javascript app)

The frontend is built in Javascript using a React/Redux stack. The project is in the `frontend/capitolwords-spa` directory and was initially created using the create-react-app tool (https://github.com/facebookincubator/create-react-app), so it should be easily updateable to newer frontend best-practices by following the upgrade path outlined in create-react-app's documentation (see the [README.md in the capitolwords-spa directory](frontend/capitolwords-spa/README.md) or read the docs on their site).

To run the frontend app, make sure you have a recent version of node installed (this is tested with node 6.9.3). I'm using [yarn](https://yarnpkg.com) instead of npm since that seems to be the norm for create-react-app. You can probably use npm (installed automatically with node) instead of yarn if you want. Just replace `yarn` with `npm` in the commands below. Do the following to get up and running:

```bash
cd frontend/capitolwords-spa
yarn install # This installs all frontend dependencies.
yarn start   # This runs the frontend development server on port 3000.
```

The frontend app depends on the APIs, so you'll need to also be running the django-based API as outlined above. The frontend development server is setup to proxy all API requests to `http://localhost:8000` -- if your django is not running on that port, or you want to proxy somewhere else, you should be able to change this by altering the `proxy` setting in the `frontend/capitolwords-spa/package.json` file. Note that you'll have to restart the frontend development server for that change to take effect.

## Data Pipeline

There are two stages to getting CREC content and metadata into Elasticsearch, the scraper and the elasticsearch uploader.

### scraper

All CREC docs for a given day are available as a zip file from gpo.gov. Metadata for these docs is available in a single xml file, `mods.xml`.

The scraper takes a date range and pulls in each zip ands mods.xml files for every day in that range (days when congress was not in session are ignored).

Example usage:

```
python run_scraper.py --start_dt=2016-01-01 --end_dt=2017-01-01 --s3_bucket=mybukkit --data_type=crec
```

This will stage all data for 2016 in the provided s3 bucket under the `capitolwords/` prefix. The rest of the key includes year, month and day, e.g.: `s3://mybukkit/crec/2017/01/03/crec/CREC-2017-01-03-pt1-PgD1.htm`.

### elasticsearch uploader

Right now, the uploader only supports CREC data. It takes a path to a mods.xml file on local disk or in S3. The modx.xml file contains metadata for each CREC document for that day. The uploader iterates through every one of those entries and reads in the corresponding CREC file from S3. The content of that file is stored along with the relevant metadata from the mods.xml in an elasticsearch document.

Example usage:

```
python run_es_uploader.py --source_path=s3://mybuckkit/crec/1994/01/25/mods/mods.xml --data_type=crec --es_url=es://<YOUR_ES_HOST>:80/<YOUR_INDEX>
```

## Workers

The instructions above cover how to use the scraper and parser/es uploader via python scripts, but they can also be scheduled as crons via the django admin ui.

The actual scheduling and configuration is pretty self-explanatory, but for things to actually execute you'll need to be running 2 celery processes, one for the scheduler and one for the workers themselves:

```
celery -A capitolweb beat -l debug -S django
```

and

```
celery -A capitolweb worker -l info
```

You may also need to run a migration for the admin ui:

```
python manage.py migrate django_celery_results
```
