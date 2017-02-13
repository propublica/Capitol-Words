#!/bin/bash
source $CAPWORDS_VENV/bin/activate
/usr/bin/env python $CAPWORDS_HOME/cwod_site/manage.py calculate_ngram_tfidf --field=year_month
