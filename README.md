Requirements
* see cwod_site/requirements.txt for python package requirements
* solr
* sunlightlabs API key

Setup:
* cp settings.example.py settings.py
* create symlinks to settings.py from each of solr/, scraper/ and parser/

* tell solr where to find the schema file. eg, if using running the dev
* environment in apache-solr-1.4.1/example/, it will uses schema.xml in the
* directory /apache-solr-1.4.1/example/solr/conf. same is true for the
* stopwords file. so set up symlinks to he real things, optionally backing up
* the originals as .example. 

cd apache-solr-1.4.1/example/solr/conf
mv schema.{,example.}xml
mv stopwords.{,example.}txt
ln -s /home/cwod/capitolwords/src/solr/schema.xml schema.xml
ln -s /home/cwod/capitolwords/src/solr/stopwords.txt stopwords.txt

Startup
* start up solr. in a dev environment this looks like:
  cd $SOLR_DIR/example
  java -jar start.jar (uses jetty)


