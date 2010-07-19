#!/usr/bin/python

import urllib, urllib2
import datetime, re, os

# note: a single day's retrieval takes about two minutes

# XXX TODO
# logging
# error handling for various ways search could fail (timeout etc.)


class CRScraper(object):	
    def __init__(self):
	# set up search params
	self.base = "http://frwebgate.access.gpo.gov/cgi-bin/multidb.cgi"
	self.params = {} 
	self.search_results = None
	self.search_date = None

    def num_search_results(self, raw):
	''' extracts the number of hits from the search results page. '''
	numhits = re.compile("<h3>Total Hits:\s?(?P<numhits>\d+)\s?</h3>")
	# subtract one from the number of hits since the last 'hit' is always
	# the query report for this search. 
	hits = int(numhits.search(raw).group('numhits')) - 1
	return hits

    def parse_results(self, raw):
	textfiles = re.compile("http://frwebgate\d\.access\.gpo\.gov/cgi-bin/TEXTgate\.cgi\?WAISdocID=(?P<doc_id>[\w/]+)\&WAISaction=retrieve")	
	results = {}
	for match in textfiles.finditer(raw):
	    # eat your greens: group 0 is always the entire matched regex
	    url, doc_id = match.group(0, 'doc_id')
	    results[doc_id] = url
	self.search_results = results


    def datesearch(self, date):
	''' performs a search for documents on the given date, passing in a
	    datetime object, and returning a list of document ids. other search
	    functions are wrappers to this one.  ''' 
	self.search_date = date
	# set up the reverse-engineered query parameters needed for the query. 
	WAISdbName = year = '%d_record Congressional Record' % date.year
	datestring = date.strftime("%d/%m/%Y")
	print 'searching for documents from %s' % datestring
	WAISqueryRule =  '(DATE=%s) AND ((SECTION=house) OR (SECTION=senate) OR (SECTION=extensions))' % datestring
	WAIStemplate = 'multidb_results.html'
	self.params = { 'WAISqueryString': '', 
			'WAISdbName': WAISdbName,
			'WAIStemplate': WAIStemplate, 
			'WAISqueryRule': WAISqueryRule,
		      }
	data = urllib.urlencode(self.params)
	raw = urllib2.urlopen(self.base, data).read()	
	numhits = self.num_search_results(raw)
	print numhits
	self.parse_results(raw)
	# save the individual documents to disk
	self.retrieve()

    def catchup(self):
	''' identifies missing documents and retrieves them'''
	pass

    def daterangesearch(self, start, end):
	pass

    def keywordsearch(self, query):
	pass

    def retrieve(self):
	''' retrieves the document with the specified document id '''
	print 'retrieving docs'
	print self.search_results
	for doc_id, ascii_url in self.search_results.iteritems():
	    save_path = '/tmp/cr/raw/%d/%d/%d/' % (self.search_date.year, self.search_date.month, self.search_date.day)
	    if not os.path.exists(save_path):
		os.makedirs(save_path)
	    doc_title = doc_id.replace('/', '-')
	    saveas = os.path.join(save_path, doc_title+'.txt')
	    if os.path.exists(saveas):
		print 'skipping existing file %s' % saveas
		continue
	    doc = urllib.urlopen(ascii_url)
	    out = open(saveas, 'w')
	    print 'saving %s...' % saveas
	    out.write(doc.read())
	    out.close() 
	    
if __name__ == '__main__':
    print '\ncongressional record scraper\n'
    while True:
        datestring = raw_input('enter a date to run the scraper for (dd/mm/yyyy): ')
	date = re.match('(?P<day>\d{2})/(?P<month>\d{2})/(?P<year>\d{4})', datestring)
        if date:
	    break
	else: print 'incorrect date format'
    date = datetime.date(int(date.group('year')), int(date.group('month')), int(date.group('day')))
    cr = CRScraper()
    cr.datesearch(date)



