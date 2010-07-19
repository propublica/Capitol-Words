#!/usr/bin/python

import urllib, urllib2, os, datetime, re, sys, httplib, zipfile
from settings import *
try:
    import json
except:
    import simplejson as json

    
class CRScraper(object):
    def __init__(self):
        # use httplib so that we can retrieve the headers before retrieving the
	    # body. 
        self.domain = "www.gpo.gov"
        self.path = "/fdsys/delivery/getpackage.action"
        self.date = None
        self.datestring = None
        self.url = None
        self.zipsize = None

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
            print 'Congress was not in session on %s' % self.datestring
            return False
        else: 
            self.zipsize = resp.getheader('content-length')
            return True

    def retrieve(self):
        tmpfile = os.path.join(TMP_DIR, "CREC-%s.zip" % self.datestring)

        # download the zipfile if we don't already have it. 
        rightsize = lambda tmfile: os.path.getsize(tmpfile) == self.zipsize
        if not os.path.exists(tmpfile) or not rightsize:
            zip = urllib.urlopen('http://' + self.domain + self.url)
            tmp = open(tmpfile, 'w')
            print 'retrieving zip file %s. this could take a few mins...' % tmpfile
            tmp.write(zip.read())
            tmp.close()
        else: print '%s exists. skipping download' % tmpfile

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
            filename = os.path.basename(f).split('.')[0]+'.txt'
            saveas = os.path.join(save_path, filename)
            if not os.path.exists(saveas):
                # re.DOTALL is important - it tells 'dot' (.) to match newline character.
                findraw = re.compile(r'<body><pre>(?P<raw>.*)</pre></body>', re.DOTALL)
                try:
                    raw = findraw.search(doc).group('raw')
                    out = open(saveas, 'w')
                    out.write(raw)
                    out.close()
                    print 'saving %s...' % saveas
                except BaseException, e:
                    print 'Problem downloading file %s. Error:' % saveas
                    print e
            else: print 'file %s already exists. skipping.' % saveas

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


