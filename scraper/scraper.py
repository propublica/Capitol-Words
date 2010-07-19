#!/usr/bin/python

import urllib, urllib2, os, datetime, re, sys, httplib, zipfile
try:
    import json
except:
    import simplejson as json

CWOD_DIR = '/tmp/cr'
    
class CRScraper(object):
    def __init__(self):
        # use httplib so that we can retrieve the headers before retrieving the
	    # body. 
        self.domain = "www.gpo.gov"
        self.path = "/fdsys/delivery/getpackage.action"
        self.date = None
        self.datestring = None
        self.url = None

    def set_date(self, date):
        ''' given a date object, retrieve the documents for that given date and
        save them to the filesystem.''' 
        self.date = date
        self.datestring = date.strftime("%Y-%m-%d")
        self.url = self.path + "?packageId=CREC-%s" % self.datestring    

    def was_in_session(self):
        # check the response header to make sure the Record exists for this date. 
        conn = httplib.HTTPConnection(self.domain)
        conn.request("HEAD", self.url)
        resp = conn.getresponse()
        content_type = resp.getheader('content-type')
        if content_type != 'application/zip':
            return False
        else: 
            return True

    def retrieve(self):
        # check to see if we have the zipfile already

        # save the zipfile
#        zip = urllib.urlopen('http://' + self.domain + self.url)
        tmpfile = "/tmp/CREC-%s.zip" % self.datestring
#        tmp = open(tmpfile, 'w')
#        print 'retrieving zip file %s. this could take a few mins...' % tmpfile
#        tmp.write(zip.read())
#        tmp.close()

        # prepare the directory to copy the zipped files into
        save_path = os.path.join(CWOD_DIR, 'raw/%d/%d/%d/' % (self.date.year, self.date.month, self.date.day))
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # iterate over the html files in the zipfile, extracting the
        # ascii-formatted <pre> section and saving the file as raw textfiles
        zip = zipfile.ZipFile(tmpfile)
        html_files = [doc for doc in zip.namelist() if doc.endswith('.htm')]   
        for f in html_files:
            doc = zip.read(f)
            # re.DOTALL is important - it tells 'dot' (.) to match newline character.
            findraw = re.compile(r'<body><pre>(?P<raw>.*)</pre></body>', re.DOTALL)
            raw = findraw.search(doc).group('raw')
            filename = os.path.basename(f).split('.')[0]+'.txt'
            saveas = os.path.join(save_path, filename)
            out = open(saveas, 'w')
            out.write(raw)
            out.close()

        # delete tmfile
        os.remove(tmpfile)

        return save_path

    def retrieve_by_date(self, date):
        self.set_date(date)
        if self.was_in_session():
            path = self.retrieve()


class ScraperManager(object):
    ''' manage scraping process '''
    
    def __init__(self, scraper_type):
        self.scraper = scraper_type
    
    def catchup(self):
        ''' checks for new or missing files and retreives them'''
        # retrieve info about state of downloaded files
        # determine which files need to be retrieved
        # retrieve them
        # update info about days (have, missing, DNE)
        pass


