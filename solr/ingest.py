#!/usr/bin/python

''' Takes XML-annotated CR documents and turns them into solr documents. The
primary difference is that solr expects fields to be in a different format, and
the coarseness of its retrieval ability is limited to documents, so for example,
if you want to limit a search result to a specific speaker, then you may only
have one speaker per solr document.'''

from httplib import HTTPConnection
import xml.dom.minidom as xml
import sys, os, re
from lib import bioguide_lookup

class SolrDoc(object):
    def __init__(self, file):
        self.filename = file
        self.dom = xml.parse(filename)
        self.metadata_xml = None
        self.document_bodies = []

    def get_text(self, uniquetag):
        ''' only use this for unique tags that appear once in the document'''
        re_tag_content = r'<.*?>(?P<content>.*?)</.*?>'
        nodexml = self.dom.getElementsByTagName(uniquetag)[0].toxml()
        text = re.search(re_tag_content, nodexml).group('content')
        return text

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
        date = "%s-%s-%sT00:00:00Z" % (year, numeric_months[month.lower()], day)
        # store the original file this came from so we can go back to it
        self.metadata_xml = '''<field name="crdoc">%s</field>''' % self.filename
        self.metadata_xml += '''<field name="date">%s</field>\n''' % date

        if self.dom.getElementsByTagName('document_title'):
            doc_title = self.get_text('document_title')
            self.metadata_xml += '''<field name="document_title">%s</field>\n''' % doc_title

        for tag in ['volume', 'number', 'chamber', 'pages']:
            tag_content = self.get_text(tag)
            self.metadata_xml += '''<field name="%s">%s</field>\n''' % (tag, tag_content)
    
    def get_metadata(self):
        return self.metadata_xml

    def get_speaker_metadata(self, speaker):
        pieces = speaker.split(' of ')
        name = pieces[0]
        lastname = name.lower().strip('msr.').strip()
        if len(pieces) > 1:
            state = pieces[1]
        else:
            state = None
        data = bioguide_lookup(lastname, self.year, state)
        print data
        print lastname, self.year, state
        print len(data)
        if not data or len(data) > 1:
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
                current_speaker = someone_speaking.group('current_speaker')
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

            speaker_line = '''<field name="speaker">%s</field>\n''' % current_speaker
            if (current_speaker != 'recorder' and not re.search('pro tempore', current_speaker) 
                and not re.search('president', current_speaker)):
                speaker_metadata = self.get_speaker_metadata(current_speaker)
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
            print solrdoc
            raw_input("enter to post...")
            self.post(solrdoc)
            self.commit()
            raw_input("enter to continue...")
        
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
            print r.read()
        else:
            print r.status
            print r.read()

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
        if str(r.status) == '200':
            print r.read()
        else:
            print r.status
            print r.read()

  
    def process(self):
        self.set_metadata()
        self.build_document_bodies()
        self.assemble_and_submit()
        

if __name__ == '__main__' :

    filename = sys.argv[1]
    s = SolrDoc(filename)
    s.process()

