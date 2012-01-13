#!/bin/bash
yesterday=`date -d '1 day ago' +'%Y/%m/%d'`

date_count_date=`date -d '1 day ago' +'%Y-%m-%d'`

# The scraper takes a different date format
scraper_yesterday=`date -d '1 day ago' +'%d/%m/%Y'`

# Scrape yesterday's record
/projects/capwords/bin/python /projects/capwords/src/Capitol-Words/scraper/scraper.py backto $scraper_yesterday

# Ingest if congress was in session
if [ -d /opt/data/raw/$yesterday ]; then

  for i in `find /opt/data/raw/$yesterday -name '*PgH*.txt'`; do
      /projects/capwords/bin/python /projects/capwords/src/Capitol-Words/parser/parser.py $i;
  done

  for i in `find /opt/data/raw/$yesterday -name '*PgS*.txt'`; do
      /projects/capwords/bin/python /projects/capwords/src/Capitol-Words/parser/parser.py $i;
  done

  for i in `find /opt/data/raw/$yesterday -name '*PgE*.txt'`; do
      /projects/capwords/bin/python /projects/capwords/src/Capitol-Words/parser/parser.py $i;
  done

  for i in `find /opt/data/xml/$yesterday -mtime -1 -name '*.xml'`; do
      /projects/capwords/bin/python /projects/capwords/src/Capitol-Words/solr/ingest.py $i --solrdocs-only;
  done

  find /opt/data/solrdocs/$yesterday -mtime -1 -name '*.xml' -exec curl -d @{} http://ec2-184-72-184-231.compute-1.amazonaws.com:8983/solr/update -H "Content-Type: text/xml" \;

  curl "http://ec2-184-72-184-231.compute-1.amazonaws.com:8983/solr/update?commit=true"

  source /projects/capwords/bin/activate
  /usr/bin/env python /projects/capwords/src/Capitol-Words/cwod_site/manage.py get_date_counts --date=$date_count_date
  /usr/bin/env python /projects/capwords/src/Capitol-Words/cwod_site/manage.py calculate_ngram_tfidf --field=date
  /usr/bin/env python /projects/capwords/src/Capitol-Words/cwod_site/manage.py cache_recent_entries

fi

# Always run these
source /projects/capwords/bin/activate
/usr/bin/env python /projects/capwords/src/Capitol-Words/cwod_site/manage.py apireportfromlogs
