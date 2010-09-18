#!/usr/bin/python

'''
The main loop for Capitol Words, run daily. 

To add to cron, add the following line to /etc/crontab:

This will run the script once a day at 3am for the previous day's files. 

'''

import datetime
from settings import *
from scraper.scraper import run_scraper
from parser.parser import CRParser
from solr.ingest import solr_ingest_dir

def run(date):
    # if congress was not in sessio or if there was a connection problem,
    # run_scraper will return None. 
    raw_files = run_scraper(date)
    if raw_files:
        xml_dir = parse_directory(raw_files)
        solr_ingest_dir(xml_dir)


# check for the most recent congression record documents
today = datetime.datetime.now()
yesterday = datetime.datetime(today.year, today.month, today.day-1)
run(yesterday)

# now check the scraper log to see if any previous files had errors, and if so,
# try to get them again. 
scraper_log = open(SCRAPER_LOG)
scraper_lines = scraper_log.readlines()
for line in scraper_lines:
    if 'errors' in line:
        datestring = line.split(',')[0].strip()
        date = datetime.datetime.strptime(datestring, "%d/%m/%Y")
        run(date)

