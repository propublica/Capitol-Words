# Capitol Words NG - The Upgrade

This will ultimately replace the top level codebase. Developed by [Chartbeat](https://www.chartbeat.com) Engineers during hackweeks!

## Setup

To set up the API do the following:

    cd Capitol-Words/capitolwords_ng/capitolweb
    python manage.py migrate
    python manage.py loadcongress
    python manage.py createsuperuser (if you want to use the admin tool to browse)
    python manage.py runserver


## The API

The API is built on Django and it's broken into 2 apps: 

    * cwapi - document search with elastic search
    * legislators - database of congress people
 
## cwapi

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

## legislators api

The legislators are pulled from the [unitedstates/congress-legislators](https://github.com/unitedstates/congress-legislators) project and stored in the database.

Endpoints:

    /legislators/search
    /legislators/person/<bioguide_id>
    /legislators/current?<state>
    
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

