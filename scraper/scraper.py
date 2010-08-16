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
        rightsize = lambda tmpfile: os.path.getsize(tmpfile) == self.zipsize
        if not os.path.exists(tmpfile) or not rightsize(tmpfile):
            zip = urllib.urlopen('http://' + self.domain + self.url)
            tmp = open(tmpfile, 'w')
            print 'retrieving zip file %s. this could take a few mins...' % tmpfile
            tmp.write(zip.read())
            tmp.close()
        else: print '%s exists. skipping download' % tmpfile

        # prepare the directory to copy the zipped files into. use strftime
        # here to ensure day and month directories are always 2 digits. 
        save_path = os.path.join(CWOD_HOME, 'raw/%d/%s/%s/' % (self.date.year,
        self.date.strftime("%m"), self.date.strftime("%d")))
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


def date_from_string(datestring):
    return datetime.datetime.strptime(datestring, "%d/%m/%Y")

if __name__ == '__main__':

    if len(sys.argv) == 1:
        datestring = raw_input("input date to retrieve dd/mm/yyyy: ")
        dates = [date_from_string(datestring)]

    elif len(sys.argv) == 2:
        dates = [date_from_string(sys.argv[1])]

    elif len(sys.argv) == 4: 
        start = date_from_string(sys.argv[1])
        end = date_from_string(sys.argv[3])
        daterange = (end - start).days
        dates = [start + datetime.timedelta(n) for n in xrange(daterange)]

    else:
        print '\ninvalid date range. date range must look like dd/mm/yyyy - dd/mm/yyyy\n'
        sys.exit()

    for date in dates:
        print "Checking Congressional Record for %s" % date
        CRScraper().retrieve_by_date(date)
