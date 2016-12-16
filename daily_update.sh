#!/bin/bash
yesterday=`date -d '1 day ago' +'%Y/%m/%d'`

date_count_date=`date -d '1 day ago' +'%Y-%m-%d'`

# The scraper takes a different date format
scraper_yesterday=`date -d '1 day ago' +'%d/%m/%Y'`

# Scrape yesterday's record
$CAPWORDS_VENV/bin/python $CAPWORDS_HOME/scraper/scraper.py backto $scraper_yesterday

source $CAPWORDS_ENV/bin/activate

# Ingest if congress was in session
if [ -d /opt/data/raw/$yesterday ]; then

  for i in `find /opt/data/raw/$yesterday -name '*PgH*.txt'`; do
      $CAPWORDS_ENV/bin/python $CAPWORDS_HOME/parser/parser.py $i;
  done

  for i in `find /opt/data/raw/$yesterday -name '*PgS*.txt'`; do
      $CAPWORDS_ENV/bin/python $CAPWORDS_HOME/parser/parser.py $i;
  done

  for i in `find /opt/data/raw/$yesterday -name '*PgE*.txt'`; do
      $CAPWORDS_ENV/bin/python $CAPWORDS_HOME/parser/parser.py $i;
  done

  for i in `find /opt/data/xml/$yesterday -mtime -1 -name '*.xml'`; do
      $CAPWORDS_ENV/bin/python $CAPWORDS_HOME/solr/ingest.py $i --solrdocs-only;
  done

  find /opt/data/solrdocs/$yesterday -mtime -1 -name '*.xml' -exec curl -d @{} $CAPWORDS_SOLR_URL/update -H "Content-Type: text/xml" \;

  curl "$CAPWORDS_SOLR_URL/update?commit=true"

  /usr/bin/env python $CAPWORDS_HOME/cwod_site/manage.py get_date_counts --date=$date_count_date
  /usr/bin/env python $CAPWORDS_HOME/cwod_site/manage.py calculate_ngram_tfidf --field=date
  /usr/bin/env python $CAPWORDS_HOME/cwod_site/manage.py cache_recent_entries

fi

# Always run these
/usr/bin/env python $CAPWORDS_HOME/cwod_site/manage.py apireportfromlogs
