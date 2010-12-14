#!/usr/bin/python

''' useful supporting functions '''

from settings import API_KEY, DB_PATH

from BeautifulSoup import BeautifulSoup
import urllib2, urllib, re

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

def bioguide_lookup(lastname, year, position=None, state=None):
    ''' looks up full name, bioguide id, state, and party based on last name, year
    and optionally, state. returns one or more results. lastname and year are
    usually all that's required to return a unique result, but with common names if
    multiple legislators have the same last name in the same congress, the state
    argument is also needed to uniquely specify. with all three, there *should*
    only be a single result.'''

    arguments = {'lastname': lastname, 'congress': year}
    if state and abbr(state):
        arguments['state'] = abbr(state).upper()
    if position:
        arguments['position'] = position.title()
    url = "http://bioguide.congress.gov/biosearch/biosearch1.asp"
    html_lines = urllib2.urlopen(url, urllib.urlencode(arguments)).readlines()
    re_result_firstline = r'<tr><td><a href="http://bioguide\.congress\.gov/scripts/biodisplay\.pl\?index=(?P<bioguide>.*?)">(?P<lastname>.*?), (?P<firstname>.*?)</a></td><td>.*?</td>'
    re_result_secondline = r'<td>.*?</td><td>(?P<party>.*?)</td><td align="center">(?P<state>\w\w)</td><td align="center">\d+<br>\((?P<startyear>\d{4})\-(?P<endyear>\d{4})\)</td></tr>'
    results = []
    for i in xrange(len(html_lines)):
        line = html_lines[i]
        matching_row = re.search(re_result_firstline, line.lower())
        if matching_row:
            data = {
                'bioguide': matching_row.group('bioguide'),
                'firstname': matching_row.group('firstname'),
                'lastname': matching_row.group('lastname'),
            }
            i+=1
            row_continued = re.search(re_result_secondline, html_lines[i].lower())
            if row_continued:
                data['party'] = row_continued.group('party')
                data['state'] = row_continued.group('state')
                data['years'] = (row_continued.group('startyear'), row_continued.group('endyear'))
            results.append(data)
    if results:
        return results
    else: return None


def db_bioguide_lookup(lastname, year, position, state=None):
    import sqlite3
    conn = sqlite3.Connection(DB_PATH)
    cursor = conn.cursor()

    congresses = {'2010': '111',
                  '2009': '111',
                  '2008': '110',
                  '2007': '110',
                  '2006': '109',
                  '2005': '109',
                  '2004': '108',
                  '2003': '108',
                  '2002': '107',
                  '2001': '107',
                  '2000': '106',
                  '1999': '106', }



    query = """SELECT bioguide_id AS bioguide,
                             party AS party,
                             state AS state,
                             first AS firstname,
                             last AS lastname
                        FROM bioguide_legislator 
                                            WHERE last = ? COLLATE NOCASE
                                            AND   congress = ?"""

    args = [lastname,
            congresses[year],
            ]
    if state:
        query += " AND state = ? COLLATE NOCASE"
        args.append(abbr(state))

    if position == 'senator':
        query += " AND position = 'Senator' "
    else:
        """Because the position passed to this function is
        determined by the chamber from which the text comes,
        delegates and resident commissioners will be missed.
        """
        query += " AND position IN ('Delegate', 'Representative', 'Resident Commissioner') "

    fields = ['bioguide', 'party', 'state', 'firstname', 'lastname', ]
    cursor.execute(query, args)
    return [dict(zip(fields, x)) for x in cursor.fetchall()]

