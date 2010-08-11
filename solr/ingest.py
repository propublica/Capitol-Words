#!/usr/bin/python

''' Takes XML-annotated CR documents and turns them into solr documents. The
primary difference is that solr expects fields to be in a different format, and
the coarseness of its retrieval ability is limited to documents, so for example,
if you want to limit a search result to a specific speaker, then you may only
have one speaker per solr document.'''

from httplib import HTTPConnection

class SolrDoc(object):
    def __init__(self, file):
        self.filename = file
        self.lines = open(filename).readlines()
        self.metadata = {
            'speaker' : None,
            'document_title' : None,
            'volume' : None,
        }
        self.documents = []

    def set_metadata(self):
        ''' each solr document generated from this CR document will share the
        same metadata. assemble a string containing that metadata.''' 
        pass

    def get_metadata(self):
        return self.metadata_string

    def speaker_split(self):
        ''' iterate over the document, and split it up anytime there is a
        change in speaker.'''
        self.current_speaker = 'empty'
        for line in self.lines:
            # figure out the first speaker or if there is none:
            speaker = self.check_speaker(line)
            if speaker_change(line):
                self.documents.append([])
            self.documents[-1].append(line)

    def speaker_change(self, line):
        ''' update the current speaker and return True if there is a speaker
        change, else return False.'''

        new_speaker = re.match(r'<speaker name="(Mr|Mrs|Ms)\. (?P<name>.*?)">'
        recorder = line.stip().startswith('<recorder>')
        if new_speaker or recorder:
            # XXX This should be expanded to include bioguide id, full name etc.
            if new_speaker:
                speaker_name = matchob.group('name')
            else:
                speaker_name = 'recorder'
            if speaker_name == self.current_speaker:
                return False
            else: 
                self.current_speaker = speaker_name
                return True  
        else:
            return False
            

    def doc_gen(self):
        ''' generate a proper solr document '''
        # add metadata
        # replace xml with proper solr fields
        for xmldoc in self.documents:
            metadata_fields = self.get_metadata()
            speaker_name = self.extract_speakername(xmldoc[1])
            speaker_fields = self.get_speakerinfo(speaker_name)) 
            body_fields = self.solrize_fields(xmldoc)
            solrdoc = metadata_fields + speaker_fields + body_fields
            self.add(solrdoc)
            self.commit()
        
        

   def add(self, item_id, title, description, text):
        """
        Add a document to index
        """
        DATA = '''<add><doc>
    <field name="id">%d</field>
    <field name="title">%s</field>
    <field name="description">%s</field>
    <field name="text">%s</field>
    </doc></add>''' % (item_id, title, description, text)
        con = HTTPConnection('0.0.0.0:8983')
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

    def commit(self):
        """
        commit changes
        """
        DATA = '<commit/>'
        con = HTTPConnection('0.0.0.0:8983')
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

    def parse(self):
        self.set_metadata()
        self.speaker_split()
        self.doc_gen()


 
