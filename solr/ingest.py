#!/usr/bin/python

''' Takes XML-annotated CR documents and turns them into solr documents. The
primary difference is that solr expects fields to be in a different format, and
the coarseness of its retrieval ability is limited to documents, so for example,
if you want to limit a search result to a specific speaker, then you may only
have one speaker per solr document.'''

from httplib import HTTPConnection
import xml.dom.minidom as xml
from xml.sax.saxutils import escape, unescape
from xml.parsers.expat import ExpatError
import sys, os, re
from lib import bioguide_lookup, db_bioguide_lookup, fallback_bioguide_lookup

import site
ROOT = os.path.dirname(os.path.realpath(__file__))
site.addsitedir(os.path.join(ROOT, "../"))
from settings import *

import datetime

import lxml.etree
import nltk

from django.template.defaultfilters import slugify


def make_ngrams(xml, filename):
    text = re.findall(r'<field name="speaking">(.*?)<\/field>', xml, re.S)

    fields = ['unigrams', 'bigrams', 'trigrams', 'quadgrams', 'pentagrams', ]
    ngrams = []

    # Identify bills at the end of sentences.
    # Should be able to train the sentence tokenizer
    # to know that bill names aren't sentence delimiters.
    bill_regex = re.compile(r'(?:H|S)\. ?(?:(?:J|R)\. ?)?(?:Con\. ?)?(?:Res\. ?)?$')

    for graf in text:
        graf = re.sub(r' +', ' ', graf.replace('\n', ' '))
        sentences = nltk.tokenize.sent_tokenize(graf)

        done = []

        for n, sentence in enumerate(sentences):

            if n in done:
                continue

            sentence = re.sub(r'<.*?>', '', unescape(sentence))

            # Handle problem of bill numbers being split into new sentences.
            if bill_regex.search(sentence):
                try:
                    if re.search(r'[0-9]+\.', sentences[n+1]):
                        sentence = ' '.join([sentence, sentences[n+1]])
                        done.append(n+1)
                except IndexError:
                    pass
            done.append(n)


            # Adapted From Natural Language Processing with Python
            regex = r'''(?x)
            (?:H|S)\.\ ?(?:(?:J|R)\.\ )?(?:Con\.\ )?(?:Res\.\ )?\d+ # Bills
          | ([A-Z]\.)+                                              # Abbreviations (U.S.A., etc.)
          | ([A-Z]+\&[A-Z]+)                                        # Internal ampersands (AT&T, etc.)
          | (Mr\.|Dr\.|Mrs\.|Ms\.)                                  # Mr., Mrs., etc.
          | \d*\.\d+                                                # Numbers with decimal points.
          | \d\d?:\d\d                                              # Times.
          | \$?[,\.0-9]+\d                                          # Numbers with thousands separators, (incl currency).
          | (((a|A)|(p|P))\.(m|M)\.)                                # a.m., p.m., A.M., P.M.
          | \w+((-|')\w+)*                                          # Words with optional internal hyphens.
          | \$?\d+(\.\d+)?%?                                        # Currency and percentages.
          | (?<=\b)\.{3,4}(?=\b)                                     # Ellipses surrounded by word borders
          | [][.,;"'?():-_`]
            '''

            # Tokenize the sentence into unigrams
            # and do some cleanup of the tokens
            words = [re.sub(r',', '', x.lower().rstrip('-').strip("'"))
                        for x in nltk.regexp_tokenize(sentence, regex)
                        if re.search(r'[a-z0-9.?!]', x.lower()) and not re.search(r'[.]{5,}', x.lower())]

            ngrams += [item for sublist in [['<field name="%s">%s</field>' % (field, escape(' '.join(ngram)))
                            for ngram in nltk.util.ngrams(words, n+1)]
                                for n, field in enumerate(fields)] for item in sublist]

    return '\n'.join(ngrams)


def find_bills(xml):
    """Find any ngrams that are bill numbers.
    """
    text = re.findall(r'<field name="speaking">(.*?)<\/field>', xml, re.S)
    regex = re.compile(r'(?:H|S)\. ?(?:(?:J|R)\. )?(?:Con\. )?(?:Res\. )?\d+')
    bills = []
    for graf in text:
        bills += regex.findall(graf)
    return '\n'.join(['<field name="bill">%s</field>' % bill for bill in set(bills)]) + '\n'


numeric_months = {
    'january' : '01',
    'february' : '02',
    'march': '03',
    'april': '04',
    'may': '05',
    'june': '06',
    'july': '07',
    'august': '08',
    'september': '09',
    'october': '10',
    'november': '11',
    'december': '12',
}


class SolrDoc(object):
    def __init__(self, file):
        self.status = None
        self.error = None
        self.warning = None
        self.filename = file
        raw = open(self.filename).read()
        # minidom doesn't properly escape ampersands!
        raw_replaced = raw.replace("&", "&amp;")
        self.dom = xml.parseString(raw_replaced)
        self.metadata_xml = None
        self.document_bodies = []

    def get_text(self, uniquetag):
        ''' only use this for unique tags that appear once in the document'''
        re_tag_content = r'<.*?>(?P<content>.*?)</.*?>'
        try:
            nodexml = self.dom.getElementsByTagName(uniquetag)[0].toxml()
        except IndexError:
            print 'get_text error. uniquetag: %s' % uniquetag
            return ''
        tag_content = re.search(re_tag_content, nodexml, re.DOTALL)
        if tag_content:
            text = tag_content.group('content')
            return text
        else:
            return ''

    def make_solr_id(self, num):
        uid = os.path.basename(self.filename).strip('xml')+'chunk%d' % num
        id_xml = '''<field name="id">%s</field>\n''' % uid
        return id_xml

    def set_metadata(self):
        ''' each solr document generated from this CR document will share the
        same metadata. assemble a string containing that metadata.'''


        # date format: 1995-12-31T23:59:59Z
        day = self.get_text('day')
        month = self.get_text('month')
        year = self.get_text('year')
        # keep the year around; we use it later to retrieve speaker metadata
        self.year = year
        # set the date. note the time is set to noon. this is to avoid setting
        # the time near the boundary of the day, since solr requires more
        # subtle handling of such date queries.
        date = "%s-%s-%sT12:00:00Z" % (year, numeric_months[month.lower()],
        day)
        page_id =  re.search(r'Pg([A-Z][-0-9]+)', self.filename).groups()[0]
        # store the original file this came from so we can go back to it
        self.metadata_xml = '''<field name="crdoc">%s</field>\n''' % self.filename
        self.metadata_xml += '''<field name="page_id">%s</field>\n''' % page_id
        self.metadata_xml += '''<field name="date">%s</field>\n''' % date
        self.metadata_xml += '''<field name="year">%s</field>\n''' % year
        self.metadata_xml += '''<field name="month">%s</field>\n''' % numeric_months[month.lower()]
        self.metadata_xml += '''<field name="day">%s</field>\n''' % self.get_text('day')
        self.metadata_xml += '''<field name="year_month">%s%s</field>\n''' % (year, numeric_months[month.lower()])

        """
        if self.dom.getElementsByTagName('document_title'):
            doc_title = self.get_text('document_title')
        else:
            doc_title = self.get_title_from_mods_file()
        """
        doc_title = self.get_title_from_mods_file()

        self.metadata_xml += '''<field name="document_title">%s</field>\n''' % doc_title
        slug = slugify(doc_title)[:50]
        self.metadata_xml += '''<field name="slug">%s</field>\n''' % slug

        for tag in ['volume', 'number', 'chamber', 'pages', 'congress', 'session',]:
            tag_content = self.get_text(tag)
            self.metadata_xml += '''<field name="%s">%s</field>\n''' % (tag, tag_content)

        # the dummy field has the same value for all documents, and provides an
        # anchor when we want to do a wildcard search on all terms in a
        # specific field.
        #self.metadata_xml += '''<field name="dummy">dummyvalue</field>\n'''

    def get_title_from_mods_file(self):
        path, filename = os.path.split(self.filename)
        granule = filename.split('.')[0]
        raw_path = path.replace('xml', 'raw')
        mods_path = os.path.join(raw_path, 'mods.xml')
        fh = open(mods_path, 'r')
        xml = fh.read().replace('xmlns="http://www.loc.gov/mods/v3" ', '')
        doc = lxml.etree.fromstring(xml)
        try:
            item = doc.xpath('//relatedItem[@ID="id-%s"]' % granule)[0]
        except IndexError:
            print 'Item not found in xml: %s' % granule

        document_title = escape(item.xpath('titleInfo/title')[0].text)
        return document_title


    def get_metadata(self):
        return self.metadata_xml

    def get_speaker_metadata(self, speaker):
        pieces = speaker.split(' of ')
        lastname = pieces[0].lower()
        if lastname.startswith('mr.') or lastname.startswith('ms.') or lastname.startswith('mrs.'):
            i = lastname.find('.')
            lastname = lastname[i+1:].strip()
        if len(pieces) > 1:
            state = pieces[1]
        else:
            state = None
        # get the chamber info
        chamber = self.get_text('chamber').lower()
        if chamber == 'senate':
            position = 'senator'
        else:
            position = 'representative'

        day = self.get_text('day')
        month = self.get_text('month')
        year = self.get_text('year')
        date = '%s-%s-%s' % (year, numeric_months[month.lower()], day)

        if chamber == 'extensions':
            chamber = 'house'

        #data = db_bioguide_lookup(lastname, self.get_text('congress'), position, state)
        data = db_bioguide_lookup(lastname, self.get_text('congress'), chamber, date, state)

        if not data or len(data) > 1:
            data = fallback_bioguide_lookup(speaker, self.get_text('congress'), position)
            if not data:
                msg = 'No data or too many responses for %s, %s, %s, %s\n' % (lastname, self.year, position, state)
                print msg
                logfile = initialize_logfile()
                logfile.write('%s: %s' % (self.filename, msg))
                logfile.flush()
                return None

        match = data[0]
        #for k, v in match.iteritems():
        #    match[k] = v.encode('utf-8')

        xml = ''
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_bioguide', match['bioguide'])
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_party', match['party'])
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_state', match['state'])
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_firstname', match['firstname'])
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_middlename', match.get('middlename', ''))
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_lastname', match['lastname'])
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_title', match['title'])
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_district', match['district'])
        return xml

    def build_document_bodies(self):
        # get the top level xml nodes
        tln = self.dom.documentElement.childNodes

        # break the CR document into sections. a new section starts when the
        # speaker changes.
        sectionstarts = []
        for node in tln:
            if node.nodeName == 'speaker' or node.nodeName == 'recorder':
                sectionstarts.append(node)
        # add a control item onto the end of this list so we don't go off the
        # end when iterating over it below.
        sectionstarts.append(None)

        sections = []
        for node_i in xrange(len(sectionstarts)):
            sections.append([])
            node = sectionstarts[node_i]
            while node is not None and node is not sectionstarts[node_i+1]:
                sections[-1].append(node.toxml())
                node = node.nextSibling
        sections.remove([])

        # now that we have our sections, replace the <speaker>, <speaking> and
        # <quote> tags with their solr equivalents
        self.document_bodies = []
        for section in sections:
            body = ''.join(section)

            # identify the current speaker
            # remove the speaker/recorder tags
            # replace <speaking> tags by <field name=speaking">
            # replace <quote> tags by <field name="quote">
            re_speaker = r'<speaker name="(?P<current_speaker>.*?)">.*?</speaker>'
            re_recorder = r'<recorder>'
            re_rollcall = r'<rollcall>'
            re_quote = r'<quote speaker=.*?>'
            re_speaking = r'<speaking (quote="true" )?(speaker|name)=.*?>'
            re_title = r'<title>'
            re_endtag = r'</.*?>'

            someone_speaking = re.search(re_speaker, body)
            if someone_speaking:
                current_speaker = someone_speaking.group('current_speaker').lower()
            else:
                current_speaker = 'recorder'
            # XXX add in more info about the speaker
            #speaker_fields = self.get_speakerinfo(current_speaker))

            body = re.sub(re_speaker, '', body)
            body = re.sub(re_recorder, '<field name="speaking">', body)
            body = re.sub(re_rollcall, '<field name="rollcall">', body)
            body = re.sub(re_quote, '<field name="quote">', body)
            body = re.sub(re_speaking, '<field name="speaking">', body)
            body = re.sub(re_title, '<field name="title">', body)
            body = re.sub(re_endtag, '</field>', body)

            speaker_line = '''<field name="speaker_raw">%s</field>\n''' % current_speaker
            if (current_speaker != 'recorder' and not re.search('pro tempore', current_speaker)
                and not re.search('president', current_speaker)
                and not re.search('presiding', current_speaker)):
                speaker_metadata = self.get_speaker_metadata(current_speaker)
                if speaker_metadata == None:
                    speaker_metadata = ''
            else:
                speaker_metadata = ''
            speaker_line = speaker_line.encode('utf-8')
            body = body.encode('utf-8')
            speaker_metadata = speaker_metadata.encode('utf-8')
            self.document_bodies.append(speaker_line + speaker_metadata + body)

    def assemble_and_submit(self):
        ''' generate a proper solr document '''
        # add metadata
        # replace xml with proper solr fields
        logfile = initialize_logfile()
        for idx, body in enumerate(self.document_bodies):
            document_id_field = self.make_solr_id(idx)
            metadata_fields = self.get_metadata()
            ngram_fields = make_ngrams(body, self.filename)
            bill_fields = find_bills(body)
            solrdoc = u'<add><doc>\n'
            solrdoc += document_id_field
            solrdoc += metadata_fields
            solrdoc += ngram_fields
            solrdoc += bill_fields
            solrdoc += unicode(body, errors='replace')
            solrdoc += '\n</doc></add>'
            #solrdoc = '''<add><doc>\n''' + document_id_field + metadata_fields + ngram_fields + bill_fields + body + '''\n</doc></add>'''
            try:
                self.save_doc(solrdoc, idx)
            except lxml.etree.XMLSyntaxError:
                print '    lxml.etree.XMLSyntaxError'
                logfile.write('%s: lxml.etree.XMLSyntaxError\n' % self.filename)
                logfile.flush()
                continue
            if sys.argv[-1] != '--solrdocs-only':
                self.post(solrdoc)
                self.commit()
        if not len(self.document_bodies):
            self.status = 'OK'
            self.warning  = 'No document body. Skipping.'

    def save_doc(self, solrdoc, idx):
        p = [SOLR_DOC_PATH, ] + os.path.split(self.filename)[0].split('/')[-3:]
        path = os.path.join(*p)
        if not os.path.exists(path):
            os.makedirs(path)
        #xml = lxml.etree.fromstring(solrdoc)
        path = os.path.join(path, '%schunk%d.xml' % (
            os.path.split(self.filename)[1].strip('xml'),
            idx)
            )
        print path
        with open(path, 'w') as fh:
            #fh.write(lxml.etree.tostring(xml, pretty_print=True))
            fh.write(solrdoc.encode('utf-8'))

    def post(self, payload):
        """ Add a document to index """
        con = HTTPConnection('ec2-184-72-184-231.compute-1.amazonaws.com:8983')
        con.putrequest('POST', '/solr/update/')
        con.putheader('content-length', str(len(payload)))
        con.putheader('content-type', 'text/xml; charset=UTF-8')
        con.endheaders()
        con.send(payload)
        r = con.getresponse()
        if str(r.status) == '200':
            self.status = 'OK'
            #print r.read()
        else:
            self.status = 'error'
            self.error = '%d: %s' % (r.status, r.read())
            #print r.status
            #print r.read()

    def commit(self):
        """ commit changes """
        DATA = '<commit/>'
        con = HTTPConnection('ec2-184-72-184-231.compute-1.amazonaws.com:8983')
        con.putrequest('POST', '/solr/update/')
        con.putheader('content-length', str(len(DATA)))
        con.putheader('content-type', 'text/xml; charset=UTF-8')
        con.endheaders()
        con.send(DATA)
        r = con.getresponse()
        if not str(r.status) == '200':
            print ' ==> There was an error committing to solr'
            print r.read()
            print r.status

    def validate(self):
        ''' checks for extraneous tags and other things which would cause solr
        to choke. needs to be run before the document is processed.'''

        def check_kids(node):
            kids = node.childNodes
            for kid in kids:
                if kid.nodeName not in valid_tags:
                    print 'replacing invalid tag %s' % kid.nodeName
                    # get it's inner contents and replace the invalid tag with
                    # what's inside it.
                    parent = kid.parentNode
                    grandkids = kid.childNodes
                    parent.removeChild(kid)
                    for node in grandkids:
                        parent.appendChild(node)
                check_kids(kid)

        valid_tags = [
            u'doc', u'add', u'#text', u'volume', u'number', u'weekday', u'month', u'day',
            u'year', u'chamber', u'pages', u'document_title', u'speaker', u'speaking',
            u'quote', u'recorder', 'title', 'rollcall', 'congress', 'session', 'bullet', ]
        root = self.dom.firstChild
        check_kids(root)

    def process(self):
        self.validate()
        self.set_metadata()
        self.build_document_bodies()
        self.assemble_and_submit()

def initialize_logfile():
    ''' returns a filelike object'''
    if not os.path.exists(os.path.join(CWOD_HOME, LOG_DIR)):
        os.mkdir(os.path.join(CWOD_HOME, LOG_DIR))
    logfile = open(os.path.join(CWOD_HOME, LOG_DIR, 'ingest.log'), 'a')
    return logfile

def solr_ingest_file(filename):
    print '***   ' + filename + '   ***'
    s = SolrDoc(filename)
    s.process()
    print 'STATUS: ', s.status
    if s.error:
        print 'Solr Ingest error: ', s.error
    if s.warning:
        print 'Solr Ingest warning: ', s.warning
    print '\n'

def solr_ingest_dir(path):
    logfile = initialize_logfile()
    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        try:
            solr_ingest_file(full_path)
        except Exception, e:
            today = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            logfile.write('%s: Error processing file %s\n' % (today, full_path))
            logfile.write('\t%s' % e)
            logfile.flush()

if __name__ == '__main__' :

    filename = sys.argv[1]
    print filename
    solr_ingest_file(filename)


