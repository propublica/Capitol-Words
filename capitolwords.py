#!/usr/bin/python

'''
The main loop for Capitol Words, run daily. 
Run the script once a day at (say) 3am, to retrieve the previous day's files. 
'''

import datetime
from settings import *
from scraper.scraper import run_scraper
from parser.parser import parse_directory
from solr.ingest import solr_ingest_dir

def run(date):
    # if congress was not in sessio or if there was a connection problem,
    # run_scraper will return None. 
    raw_files = run_scraper(date)
    if raw_files:
        xml_dir = parse_directory(raw_files)
        solr_ingest_dir(xml_dir)


if __name__ == '__main__':
    # check for the most recent congression record documents
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(1)
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

