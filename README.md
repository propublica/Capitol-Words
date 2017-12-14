# Capitol Words NG - The Upgrade

Developed by [Chartbeat](https://www.chartbeat.com) Engineers during hackweeks!


## The API

The API is built on Django and it's broken into the following apps:

    * cwapi - document search with elastic search
    * legislators - database of congress people
    * scraper - service to scrape CREC documents from gpo.gov and stage them in s3
    * parser - service to extract metadata from CREC documents and upload to elasticsearch and rds

### Setup

Most of the ops related settings are setup via the django settings module.

For the elasticsearch cluster, `ES_URL` and `ES_CW_INDEX` need to contain the url with port for an elasticsearch cluster and the name of an index (this is used for both reading with the API and uploading to with the parser).

To set up the API do the following:

    cd Capitol-Words/capitolweb
    python manage.py migrate
    python manage.py loadcongress
    python manage.py createsuperuser (if you want to use the admin tool to browse)
    python manage.py runserver

See the "Frontend" section for setting up the single page frontend app.

### cwapi

The search API is backed by elastic search and uses [elasticsearch-dsl-py](https://github.com/elastic/elasticsearch-dsl-py)

There are three endpoints supported:

    1. `cwapi/term_counts_by_day/`
        - Counts the occurrences of a provided term in all CREC docs over a given time period and returns the total count per day over that date range.
        - Args:
            - `start_date`: A timestamp for the start of a date range filter, format: YYYY-MM-DD (inclusive).
            - `end_date`: End of date range filter, format: YYYY-MM-DD (inclusive).
            - `days_ago`: Number of days before the current date to retrieve results for.
            - `term`: A search term (or terms, space separated) to count occurrences for.
        - Example:
            - Request: `http://localhost:8000/cwapi/term_counts_by_day/?term=russia&start_date=2017-03-01&end_date=2017-03-30`
            - Response:
                ```json
                {
                  "status": "success",
                  "data": {
                    "daily_counts": {
                      "2017-03-01": 5,
                      "2017-03-02": 45,
                      "2017-03-03": 0,
                      "2017-03-04": 0,
                      "2017-03-05": 0,
                      "2017-03-06": 1,
                      "2017-03-07": 2,
                      "2017-03-08": 3,
                      "2017-03-09": 1,
                      "2017-03-10": 0,
                      "2017-03-11": 0,
                      "2017-03-12": 0,
                      "2017-03-13": 1,
                      "2017-03-14": 0,
                      "2017-03-15": 20,
                      "2017-03-16": 3,
                      "2017-03-17": 0,
                      "2017-03-18": 0,
                      "2017-03-19": 0,
                      "2017-03-20": 1,
                      "2017-03-21": 0,
                      "2017-03-22": 3,
                      "2017-03-23": 33,
                      "2017-03-24": 0,
                      "2017-03-25": 0,
                      "2017-03-26": 0,
                      "2017-03-27": 10,
                      "2017-03-28": 25,
                      "2017-03-29": 29,
                      "2017-03-30": 26
                    }
                  }
                }
                ```
    2. `cwapi/search/`
        - Performs elasticsearch match queries using the provided terms.
        - Args:
            - `start_date`: A timestamp for the start of a date range filter, format: YYYY-MM-DD (inclusive).
            - `end_date`: End of date range filter, format: YYYY-MM-DD (inclusive).
            - `days_ago`: Number of days before the current date to retrieve results for.
            - `title`: Search for docs with this value in the "title" of the CREC doc. 
            - `speaker`: Search for docs with this speaker listed in the CREC doc.
            - `content`: Search for docs that contain this value in the body of the CREC doc.
        - Example:
            - Request: `http://localhost:8000/cwapi/search/?content=russia&start_date=2017-03-01&end_date=2017-03-30&size=1`
            - Response:
                ```json
                {
                    "status": "success",
                    "data": [
                        {
                            "title": "RUSSIA AND TRUMP CAMPAIGN INVESTIGATION",
                            "title_part": "Senate",
                            "date_issued": "2017-03-30",
                            "content": "...",
                            "crec_id": "id-CREC-2017-03-30-pt1-PgS2140",
                            "pdf_url": "https://www.gpo.gov/fdsys/pkg/CREC-2017-03-30/pdf/CREC-2017-03-30-pt1-PgS2140.pdf",
                            "html_url": "https://www.gpo.gov/fdsys/pkg/CREC-2017-03-30/html/CREC-2017-03-30-pt1-PgS2140.htm",
                            "page_start": "S2140",
                            "page_end": "S2141",
                            "speakers": "Tom Udall,Jon Tester",
                            "segments": [
                                {
                                    "id": "id-CREC-2017-03-30-pt1-PgS2140-1",
                                    "text": "RUSSIA AND TRUMP CAMPAIGN INVESTIGATION. "
                                },
                                {
                                    "id": "id-CREC-2017-03-30-pt1-PgS2140-2",
                                    "speaker": "Mr. UDALL",
                                    "text": "...",
                                    "bioguide_id": "U000039"
                                },
                                {
                                    "id": "id-CREC-2017-03-30-pt1-PgS2140-3",
                                    "speaker": "The PRESIDING OFFICER",
                                    "text": "..."
                                },
                                {
                                    "id": "id-CREC-2017-03-30-pt1-PgS2140-4",
                                    "speaker": "Mr. TESTER",
                                    "text": "...""
                                    "bioguide_id": "T000464"
                                },
                                {
                                    "id": "id-CREC-2017-03-30-pt1-PgS2140-5",
                                    "speaker": "The PRESIDING OFFICER",
                                    "text": "...""
                                }
                            ],
                            "score": 7.5042105
                        },
                    ]
                }
                ```
    3. `cwapi/count`
        - Uses the same methods as #1 and #2 to return the collected data for a search results page. This includes daily histograms for the current period and the previous one, as well as one page of the documents themselves. Currently only supports searching the "content" field of the CREC docs.
        - Args:
            - `start_date`: A timestamp for the start of a date range filter, format: YYYY-MM-DD (inclusive).
            - `end_date`: End of date range filter, format: YYYY-MM-DD (inclusive).
            - `days_ago`: Number of days before the current date to retrieve results for.
            - `term`: A search term (or terms, space separated) to search by (in the "content" field) and count occurrences.
    
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

Data ingestion consists of a scraper that pulls in CREC data from gpo.gov then stages it in S3 and a parser that reads that staged S3 data extracts some additional metadata then uploads those documents to elasticsearch.

The staging location in S3 is determined by the following settings in the main capitolweb settings file:
    
    * `CREC_STAGING_S3_BUCKET`: Name of S3 bucket to stage files in.
    * `CREC_STAGING_S3_ROOT_PREFIX`: All S3 keys for files will be prefixed with this value.

The key format is a combination of the value of `CREC_STAGING_S3_ROOT_PREFIX`, the date the files were recorded for ("dateIssued" in the mods.xml metadata), and the filename within the gpo.gov zip file.

### scraper

All CREC docs for a given day are available as a zip file from gpo.gov. Metadata for these docs is available in a single xml file, `mods.xml`, contained within that zip file.

The scraper takes a date range and pulls in each zip file for every day in that range (days when congress was not in session are ignored). Its run through a custom django manage command:

```
./manage.py run_crec_scraper --start_date=2016-01-20 --end_date=2016-01-21
```

### parser

The parser looks up the mods.xml file in the staged S3 data and extracts the metadata specific to each CREC document. It also does some NLP analysis of the content of each document. The resulting parsed data is uploaded to elasticsearch and the django configured db.

Example usage:

```
./manage.py run_crec_parser --start_date=2016-01-20 --end_date=2016-01-21
```

### Tests

Most of the test cases included are integration tests that required a live elasticsearch cluster configured in the django settings file. A separate test index is defined in the `capitolweb.settings_test` module. `manage.py` has been modified to ensure that running `./manage.py test` will override any environment variable settings and always use the test settings.

You should be able run the scraper and parser tests without any external dependencies as they rely on [moto](https://github.com/spulec/moto) to mock out S3 operations.
