#!/usr/bin/python

import urllib, urllib2, os, datetime, re, sys, httplib, zipfile
import time
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
        conn = httplib.HTTPConnection(self.domain, timeout=25)
        conn.request("HEAD", self.url)
        # the connection can be a little dodgy, let it try connecting a few
        # times if needed. 
        could_not_connect = 0
        while could_not_connect < 3:
            try:
                resp = conn.getresponse()
                could_not_connect = False
                break
            except:
                could_not_connect += 1
        if could_not_connect:
            return None

        content_type = resp.getheader('content-type')
        if content_type != 'application/zip':
            print 'Congress was not in session on %s' % self.datestring
            return False
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
        num_expected_files = len(html_files)
        errors = 0
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
                    errors += 1
                    print 'Problem downloading file %s. Error:' % saveas
                    print e
            else: print 'file %s already exists. skipping.' % saveas
        
        # do some sanity checking
        if errors or len(os.listdir(save_path)) != num_expected_files:
            status = "errors"
        else:
            status = "success"
        self.log_download_status(self.date.strftime("%d/%m/%Y"), status)

        # delete tmfile
        os.remove(tmpfile)

        return save_path

    def log_download_status(self, datestring, status):
        if not os.path.exists(SCRAPER_LOG):
            if not os.path.exists(LOG_DIR):
                os.makedirs(LOG_DIR)
            scraper_log = open(SCRAPER_LOG, 'w')
            scraper_log.write('Date, Status\n')
            scraper_log.close()

        scraper_log = open(SCRAPER_LOG, 'r')
        scraper_lines = scraper_log.readlines()
        scraper_log.close()
        update_line = None
        # if this date is already in the log file, update it. 
        for linenum, logline in enumerate(scraper_lines):
            if datestring in logline:
                # update the status of that line 
                update_line = linenum
        if update_line:
            scraper_lines[update_line] = '%s, %s\n' % (datestring, status)
        # if the date was not already in the log file, append it at the end
        else:
            scraper_lines.append('%s, %s\n' % (datestring, status))
        scraper_log = open(SCRAPER_LOG, 'w')
        scraper_log.writelines(scraper_lines)
        scraper_log.close()

    def previously_retrieved(self):
        datestring = self.date.strftime("%d/%m/%Y")
        if not os.path.exists(SCRAPER_LOG):
             return False
        scraper_lines = open(SCRAPER_LOG).readlines()
        for line in scraper_lines:
            if datestring in line and 'success' in line:
                print 'This date was previously retrieved: Record already exists\n'
                return True
            if datestring in line and 'nosession' in line:
                print 'This date was previously retrieved: Congress was not in session.\n'
                return True
        return False

    def retrieve_by_date(self, date):
        self.set_date(date)
        if not self.previously_retrieved():
            in_session = self.was_in_session()
            if in_session:
                path = self.retrieve()
                return path
            elif in_session == False:
                datestring = self.date.strftime("%d/%m/%Y")
                self.log_download_status(datestring, 'nosession')
            elif in_session == None:
                self.log_download_status(self.date.strftime("%d/%m/%Y"), 'GPO connection error')

def date_from_string(datestring):
    return datetime.datetime.strptime(datestring, "%d/%m/%Y")

def daterange_list(start, end):
    ''' returns a list of date objects between a start and end date. start must
    come before end. '''
    daterange = (end - start).days
    dates = [start + datetime.timedelta(n) for n in xrange(daterange)]
    return dates

def usage():
    return ''' 
Several ways to invoke the scraper:

0. "./scraper.py" will display this message (and do nothing)

1. "./scraper.py all" will go back in time retrieving all daily congressional records until the date specified as OLDEST_DATE in settings.py. You probably want to use this with caution, but it can be useful during initial setup. 

2. "./scraper.py backto dd/mm/yyyy" will retrieve congressional records back to the date given. 

3. "./scraper.py dd/mm/yyyy - dd/mm/yyyy" will retreive congressional records for all days within the range given. the first date should occur before the second date in time. 

4. "./scraper.py dd/mm/yyyy" will retreive the congressional record for the day given.
    '''

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print usage()
        sys.exit()
    try:
        if len(sys.argv) == 2:
            if sys.argv[1] == 'all':
                end = datetime.datetime.now()
                start = date_from_string(OLDEST_DATE)
                dates = daterange_list(start, end)
            else:
                dates = [date_from_string(sys.argv[1])]

        elif len(sys.argv) == 3 and sys.argv[1] == 'backto':
            end = datetime.datetime.now()
            start = date_from_string(sys.argv[2])
            dates = daterange_list(start, end)

        elif len(sys.argv) == 4: 
            start = date_from_string(sys.argv[1])
            end = date_from_string(sys.argv[3])
            dates = daterange_list(start, end)

        else:
            raise Exception

    except Exception, e:
        print usage()
        print 'There was an error: ', e
        sys.exit()

    for date in dates:
        print "Checking Congressional Record for %s" % date
        if CRScraper().retrieve_by_date(date):
            print 'Will now sleep for one minute before retrieving next record...zzz...'
            time.sleep(60) 
        else:
            if len(dates) == 1:
                sys.exit()
            else:
                print 'sleeping for 5 seconds...zzz...' 
                time.sleep(5)
