source /projects/capwords/bin/activate
/usr/bin/env python /projects/capwords/src/Capitol-Words/cwod_site/manage.py calculate_ngram_tfidf --field=speaker_bioguide
/usr/bin/env python /projects/capwords/src/Capitol-Words/cwod_site/manage.py calculate_ngram_tfidf --field=speaker_state
/usr/bin/env python /projects/capwords/src/Capitol-Words/cwod_site/manage.py calculate_distance --field=state
/usr/bin/env python /projects/capwords/src/Capitol-Words/cwod_site/manage.py calculate_distance --field=bioguide