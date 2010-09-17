#!/usr/bin/python

''' Takes XML-annotated CR documents and turns them into solr documents. The
primary difference is that solr expects fields to be in a different format, and
the coarseness of its retrieval ability is limited to documents, so for example,
if you want to limit a search result to a specific speaker, then you may only
have one speaker per solr document.'''

from httplib import HTTPConnection
import xml.dom.minidom as xml
from xml.parsers.expat import ExpatError
import sys, os, re
from lib import bioguide_lookup

class SolrDoc(object):
    def __init__(self, file):
        self.status = None
        self.error = None
        self.warning = None
        self.filename = file
        raw = open(filename).read()
        # minidom doesn't properly escape ampersands!
        raw_replaced = raw.replace("&", "&amp;")
        self.dom = xml.parseString(raw_replaced)
        self.metadata_xml = None
        self.document_bodies = []

    def get_text(self, uniquetag):
        ''' only use this for unique tags that appear once in the document'''
        re_tag_content = r'<.*?>(?P<content>.*?)</.*?>'
        nodexml = self.dom.getElementsByTagName(uniquetag)[0].toxml()
        tag_content = re.search(re_tag_content, nodexml, re.DOTALL)
        if tag_content:
            text = tag_content.group('content')
            return text
        else:
            return None

    def make_solr_id(self, num):
        uid = os.path.basename(self.filename).strip('xml')+'chunk%d' % num
        id_xml = '''<field name="id">%s</field>\n''' % uid
        return id_xml

    def set_metadata(self):
        ''' each solr document generated from this CR document will share the
        same metadata. assemble a string containing that metadata.''' 
        
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
        # store the original file this came from so we can go back to it
        self.metadata_xml = '''<field name="crdoc">%s</field>\n''' % self.filename
        self.metadata_xml += '''<field name="date">%s</field>\n''' % date

        if self.dom.getElementsByTagName('document_title'):
            doc_title = self.get_text('document_title')
            self.metadata_xml += '''<field name="document_title">%s</field>\n''' % doc_title

        for tag in ['volume', 'number', 'chamber', 'pages']:
            tag_content = self.get_text(tag)
            self.metadata_xml += '''<field name="%s">%s</field>\n''' % (tag, tag_content)
   
        # the dummy field has the same value for all documents, and provides an
        # anchor when we want to do a wildcard search on all terms in a
        # specific field. 
        self.metadata_xml += '''<field name="dummy">dummyvalue</field>\n''' 
        
    
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

        # add some redundancy into the bioguide lookup (servers can be sketchy)
        tries = 1
        data = False # use False because bioguide_lookup returns None if no data found.
        while data == False and tries < 3:
            try:
                data = bioguide_lookup(lastname, self.year, position, state)
            except:
                tries += 1

        if not data or len(data) > 1:
            print data
            print 'No data or too many responses for %s, %s, %s, %s' % (lastname, self.year, position, state)
            return None
        xml = ''
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_bioguide', data[0]['bioguide'])
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_party', data[0]['party'])
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_state', data[0]['state'])
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_firstname', data[0]['firstname'])
        xml += '''<field name="%s">%s</field>\n''' % ('speaker_lastname', data[0]['lastname'])
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
            re_quote = r'<quote speaker=.*?>'
            re_speaking = r'<speaking name=.*?>'
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
            body = re.sub(re_quote, '<field name="quote">', body)
            body = re.sub(re_speaking, '<field name="speaking">', body)
            body = re.sub(re_title, '<field name="title">', body) 
            body = re.sub(re_endtag, '</field>', body)

            speaker_line = '''<field name="speaker_raw">%s</field>\n''' % current_speaker
            if (current_speaker != 'recorder' and not re.search('pro tempore', current_speaker) 
                and not re.search('president', current_speaker) and not re.search('presiding', current_speaker)):
                speaker_metadata = self.get_speaker_metadata(current_speaker)
                if speaker_metadata == None:
                    speaker_metadata = ''
            else: speaker_metadata = ''
            self.document_bodies.append(speaker_line + speaker_metadata + body)

    def assemble_and_submit(self):
        ''' generate a proper solr document '''
        # add metadata
        # replace xml with proper solr fields
        for idx, body in enumerate(self.document_bodies):
            document_id_field = self.make_solr_id(idx)
            metadata_fields = self.get_metadata()
            solrdoc = '''<add><doc>\n''' + document_id_field + metadata_fields + body + '''\n</doc></add>'''
            self.post(solrdoc)
            self.commit()
        if not len(self.document_bodies):
            self.status = 'OK'
            self.warning  = 'No document body. Skipping.'
                
    def post(self, payload):
        """
        Add a document to index
        """
        con = HTTPConnection('localhost:8983')
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
        """
        commit changes
        """
        DATA = '<commit/>'
        con = HTTPConnection('localhost:8983')
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
            u'quote', u'recorder', 'title']
        root = self.dom.firstChild
        check_kids(root)
    
    def process(self):
        self.validate()
        self.set_metadata()
        self.build_document_bodies()
        self.assemble_and_submit()
        

if __name__ == '__main__' :

    filename = sys.argv[1]
    print '***   ' + filename + '   ***'
    #try:
    s = SolrDoc(filename)
    s.process()
    print 'STATUS: ', s.status
    if s.error:
        print 'Solr Ingest error: ', s.error
    if s.warning:
        print 'Solr Ingest warning: ', s.warning
    #except ExpatError, e:
    #    print 'XML Error: %s' % e
    print '\n'

