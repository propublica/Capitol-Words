#!/usr/bin/python

''' useful supporting functions '''

from settings import API_KEY

from BeautifulSoup import BeautifulSoup
import urllib2
import urllib
try:
    import json
except:
    import simplejson as json


def abbr(longname):
    ''' return the abbreviation for a state'''
    states = {
        'alabama':'al',
        'alaska':'ak',
        'american samoa':'as',
        'arizona':'az',
        'arkansas':'ar',
        'california':'ca',
        'colorado':'co',
        'connecticut':'ct',
        'delaware':'de',
        'district of columbia':'dc',
        'florida':'fl',
        'guam':'gu',
        'georgia':'ga',
        'hawaii':'hi',
        'idaho':'id',
        'illinois':'il',
        'indiana':'in',
        'iowa':'ia',
        'kansas':'ks',
        'kentucky':'ky',
        'louisiana':'la',
        'maine':'me',
        'maryland':'md',
        'massachusetts':'ma',
        'michigan':'mi',
        'minnesota':'mn',
        'mississippi':'ms',
        'missouri':'mo',
        'montana':'mt',
        'nebraska':'ne',
        'nevada':'nv',
        'new hampshire':'nh',
        'new jersey':'nj',
        'new mexico':'nm',
        'new york':'ny',
        'north carolina':'nc',
        'north dakota':'nd',
        'northern mariana islands':'mp',
        'ohio':'oh',
        'oklahoma':'ok',
        'oregon':'or',
        'pennsylvania':'pa',
        'puerto rico':'pr',
        'rhode island':'ri',
        'south carolina':'sc',
        'south dakota':'sd',
        'tennessee':'tn',
        'texas':'tx',
        'utah':'ut',
        'vermont':'vt',
        'virgin islands':'vi',
        'virginia':'va',
        'washington':'wa',
        'west virginia':'wv',
        'wisconsin':'wi',
        'wyoming':'wy',
    }

    if longname.lower() in states.keys():
        return states[longname]
    else:
        return None

def sunlight_lookup(lastname, state=None):
    ''' attempt to determine the bioguide_id of this legislator, or
    return None. '''

    arguments = urllib.urlencode({'apikey': API_KEY, 'name': lastname, 'all_legislators': 1 })
    url = "http://services.sunlightlabs.com/api/legislators.search.json?"
    api_call = url + arguments
    print api_call
    fp = urllib2.urlopen(api_call)
    js = json.loads(fp.read())
    if (len(js['response']['results'])) > 0:
        results = js['response']['results']
    else: 
        return None

    # if state information was passed in, use it to verify that this is the
    # right legislator. otherwise, just take the best (0th) match. 
    legislator = None
    if not abbr(state):
        legislator = results[0]['result']['legislator']
        return legislator
    else:
        for result in results:
            if result['result']['legislator']['state'].lower() != abbr(state).lower():
                continue
            else:
                print 'matched!'
                legislator = result['result']['legislator'] 
                return legislator

def bioguide_lookup(lastname, state=None):
    ''' to be used if the sunlight API did not have data about this legislator'''

    # search the site
    arguments = {'lastname': lastname}
    if abbr(state):
        arguments['state'] = abbr(state).upper()
    url = "http://bioguide.congress.gov/biosearch/biosearch1.asp"
    fp = urllib2.urlopen(url, urllib.urlencode(arguments))
    print fp.read()


def temp():

    # scrape the results page
    # get info about each of them
    # store it locally for next time?

    # scrape congress's bioguide site for years of service and official bio
    html = urllib2.urlopen("http://bioguide.congress.gov/scripts/biodisplay.pl?index=%s" % bioguide_id).read()
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    yrs_of_service = soup.findAll('table')[1].find('tr').findAll('td')[1].findAll('font')[2].next.next.next.strip()
    bio_a = soup.findAll('table')[1].find('tr').findAll('td')[1].find('p').find('font').extract().renderContents()
    bio_b = soup.findAll('table')[1].find('tr').findAll('td')[1].find('p').renderContents()
    biography = bio_a.strip()+' '+bio_b.strip()

    # other metadata - from sunlightlabs services
    arguments = urllib.urlencode({'apikey': API_KEY,
                                  'bioguide_id': bioguide_id,
                                  'all_legislators': 1,
                                  })
    url = "http://services.sunlightlabs.com/api/legislators.get.json?"
    api_call = url + arguments
    print api_call
    fp = urllib2.urlopen(api_call)
    js = json.loads(fp.read())
    meta = js['response']['legislator']

    # append additional info and return
    meta['photo_url'] = photo_url
    meta['yrs_of_service'] = yrs_of_service
    meta['biography'] = biography
    return meta


