
## Getting started

Listed below are the public methods currently supported by the Capitol Words API. All requests must be signed with a valid Sunlight labs API key. You can register for one here: <http://services.sunlightlabs.com/accounts/register>

### Discussion & Bugs

Sunlight API discussion takes place at the [sunlightlabs-api-discuss google group](https://groups.google.com/forum/#!forum/sunlightlabs-api-discuss). You can ask questions there, as well as alert the maintainers of bugs. If you have specific issues with the Capitol Words API, you can open a ticket directly at [github](http://github.com/sunlightlabs/Capitol-Words/issues).

### Endpoints

All endpoints below are relative to this page, the API root. So, to make a request to the dates.json endpoint, you'd use the url `http://capitolwords.org/api/dates.json?apikey=<YOUR_KEY>`.


<a id="standard-arguments"></a>

---

## Standard arguments

All of the endpoints pulling from Solr support a set of standard arguments, 
all of which are optional. Endpoints with support for standard arguments will 
be flagged as such below.

* `state`
    
    Limit results to members of Congress from the given state.
    
    Valid values: 2-letter state abbreviation, such as MD, VA, DC.

* `party`
    
    Limit results to members of Congress from the given party.
    
    Valid values: R, D, I

* `chamber`

    The chamber to search. Default includes House, Senate and extensions of 
    remarks.

    Valid values:

    * house
    * senate
    * extensions

* `date`

    Show results for only the given date.

* `start_date`

    Limit results to those on or after the given date.

* `end_date`

    Limit results to those on or before the given date.

<a id="dates.json"></a>

---

## dates.json

Find the popularity of a phrase over a period of time. Standard arguments are supported.

### Required arguments

* `phrase`

    The phrase to search for.


### Optional arguments

* `bioguide`
    
    Limit results to the member of Congress with the given Bioguide ID.


* `mincount`
    
    Only return results where mentions are at or above the supplied threshold

* `percentages`
    
    Include the percentage of mentions versus total words in the result 
    objects.
    
    Valid values: true, **false** (default).

* `granularity`
    
    The length of time covered by each result.
    
    Valid values:
    
    * year
    * month
    * **day** (default)

### Examples

* Get a list of how many times the phrase "united states" appears in the
  Congressional Record on each day in the most recent Congress:
    
    `dates.json?phrase=united+states&apikey=<YOUR_KEY>`

* Get a list of how many times the phrase "united states" was said by
  legislators from Virginia on each day of the most recent Congress:
    
    `dates.json?phrase=united+states&entity_type=state&entity_value=VA&apikey=<YOUR_KEY>`

* Get a list of how many times the phrase "united States" appears in the
  Congressional Record on each day between Jan. 1, 2010, and June 1, 2010:
    
    `dates.json?phrase=united+states&start_date=2009-01-01&end_date=2009-06-01&apikey=<YOUR_KEY>`

* Get a list of how many times the phrase "united states" appears in the Congressional Record in each month between January and June, 2010:
    
    `dates.json?phrase=united+states&start_date=2009-01-01&end_date=2009-04-30&granularity=month&apikey=<YOUR_KEY>`

### Results

Returns a list of date objects with associated mention data
    
    {
        "results": [
            {
                "count": 14.0,
                "percentage": 0.058309037900874633,
                "total": 24010,
                "day": "1996-01-02",
                "raw_count": 14.0
            },
            {
                "count": 122.0,
                "percentage": 0.067791336044986786,
                "total": 179964,
                "day": "1996-01-04",
                "raw_count": 122.0
            },
            {
                "count": 198.0,
                "percentage": 0.13499693188791165,
                "total": 146670,
                "day": "1996-01-05",
                "raw_count": 198.0
            },
            {
                "count": 1.0,
                "percentage": 0.098135426889106966,
                "total": 1019,
                "day": "1996-01-08",
                "raw_count": 1.0
            },
            ...
        ]
    }

<a id="phrases.json"></a>

---

## phrases.json

List the top phrases for a facet.

### Required arguments

* `entity_type `
    
    The entity type to get top phrases for.
    
    Valid values:
    
    * date
    * month
    * state
    * legislator

* `entity_value`
    
    The value of the entity given in entity_type. Formats are as follows:
    
    * **date:** 2011-11-09
    * **month:** 201111
    * **state:** NY
    * **legislator (bioguide):** L000551

### Optional arguments

* `n`
    
    The size of phrase, in words, to search for (up to 5).

* `page`
    
    The page of results to show.
    
    100 results are shown at a time. To get more than 100 results, use the
    page parameter.

* `sort`
    
    The metric and direction to sort by.
    
    Valid values:
    
    * **tfidf** (default) 
    * count
    
    Both a metric and direction must be supplied, such as 'sort=count asc'

### Examples

* List the top words in July 2010 by count:
    
    `/phrases.json?entity_type=month&entity_value=201007&sort=count+desc&apikey=<YOUR_KEY>`

* List the top words for Nevada:
    
    `/phrases.json?entity_type=state&entity_value=NV&apikey=<YOUR_KEY>`

* List the top words for Barbara Lee:
    
    `/phrases.json?entity_type=legislator&entity_value=L000551&apikey=<YOUR_KEY>`

### Results

Returns a list of phrases with tf-idf and count data

    [
        {
            "tfidf": 3.8596557124800003e-05,
            "count": 5373,
            "ngram": "people"
        },
        {
            "tfidf": 1.30267768302e-05,
            "count": 3637,
            "ngram": "one"
        },
        {
            "tfidf": 2.52066478599e-05,
            "count": 3509,
            "ngram": "jobs"
        },
        {
            "tfidf": 1.17409333103e-05,
            "count": 3278,
            "ngram": "american"
        },
        ...
    ]


<a id="phrases/entity.json"></a>

---

## phrases/{entity}.json

Get the top (legislator|state|party|bioguide\_id|volume|chamber)s for a 
phrase. Standard arguments are supported.

### Required arguments

* `phrase`
    
    The phrase to search for.

### Optional arguments

* `mincount`

    Only return results where mentions are at or above the supplied threshold

* `per_page`
    
    The number of results to return per page. The maximum is 50.

* `page`
    
    The page number to return.

* `sort`
    
    The metric on which to sort top results.
    **Note: direction is not supported on this endpoint, results are always 
    returned in descending order.**

## Examples

* List the top 10 legislators for the phrase 'free market' by raw count:
    
    `/phrases/legislator.json?phrase=free+market&sort=count&per_page=10&apikey=<YOUR_KEY>`

* Find the chamber that says 'salary increase' the most:
    
    `/phrases/chamber.json?phrase=salary+increase&sort=count&apikey=<YOUR_KEY>`

### Results

Returns a list of _entity_ objects with associated count data

    {
        "results": [
            {
                "count": 41.0,
                "chamber": "House"
            },
            {
                "count": 35.0,
                "chamber": "Senate"
            },
            {
                "count": 9.0,
                "chamber": "Extensions"
            }
        ]
    }


<a id="text.json"></a>

---

## text.json

Full-text search. Standard arguments are supported

### Required arguments

No single argument is required to this endpoint; however, at least one of the text search arguments should be supplied.

### Text search arguments

* `phrase`
    
    A phrase to search the body of each CR document for.

* `title`
    
    A phrase to search the title of each CR document for.

### Optional arguments

* `bioguide`
    
    Limit results to the member of Congress with the given Bioguide ID.

* `cr_pages`
    
    The pages in the Congressional Record to search.

* `page`
    
    The page of results to show, 100 results are shown at a time.

### Examples

* Get a list of pieces of text with the phrase "obama administration" in them:
    
    `/text.json?phrase=obama+administration&apikey=<YOUR_KEY>`

* Get a list of pieces of text by Republicans with the phrase "health care debate" in them:

    `/text.json?phrase=health+care+debate&party=R&apikey=<YOUR_KEY>`

### Results

Returns a list of CR Documents and the total number found

    
    {
        "num_found": 347,
        "results": [
            {
                "speaker_state": "NC",
                "speaker_first": "Virginia",
                "congress": 111,
                "title": "CULTIVATING AMERICAN ENERGY RESOURCES",
                "origin_url": "http://origin.www.gpo.gov/fdsys/pkg/CREC-2009-07-30/html/CREC-2009-07-30-pt1-PgH9197.htm",
                "number": 117,
                "pages": "H9197-H9203",
                "volume": 155,
                "chamber": "House",
                "session": 1,
                "speaking": [
                    "Well, I think that this is a great segue to talk about the other subject that we wanted to talk about tonight, which is health care, and what is happening with the health care debate."
                ],
                "capitolwords_url": "http://capitolwords.org/date/2009/07/30/H9197_cultivating-american-energy-resources/",
                "speaker_party": "R",
                "date": "2009-07-30",
                "bills": null,
                "bioguide_id": "F000450",
                "order": 14,
                "speaker_last": "Foxx",
                "speaker_raw": "ms. foxx"
            },
            ...
        ]
    }
