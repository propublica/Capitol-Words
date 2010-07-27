#!/usr/bin/python

''' Parse the plain text version of congressional record documents and mark them up with xml.'''

import re, datetime, os, sys

class Regex(object):

    def __init__(self, string):
        self.string = string
        # a list of tuples containing (regex_string, xml_opening_tag)
        self.opentags = []
        self.closetags = []

    def insert_before(self, re_string, tag, group=None):
        # start tags are inserted at the start of a regex match. if group is
        # specified, matched at the beginning of the group instead. 
        self.opentags.append((re_string, tag, group))
    
    def insert_after(self, re_string, tag, group=None):
        # start tags are inserted at the start of a regex match. if group is
        # specified, matched at the end of the group instead. 
        self.closetags.append((re_string, tag, group))


    def apply(self):
        indexes = {}
        # identify where all the opening tags go (those that get inserted at
        # the start of the regex match)
        for regex, tag, group in self.opentags:
            matchobj = re.search(regex, self.string)
            if matchobj: 
                if group:
                    start = matchobj.start(group)
                else:
                    start = matchobj.start()
                indexes[start] = tag
        # identify where all the closing tags go (those that get inserted at
        # the end of the regex match)
        for regex, tag, group in self.closetags:
            matchobj = re.search(regex, self.string)
            if matchobj:
                if group:
                    end = matchobj.end(group)
                else:
                    end = matchobj.end()
                indexes[end] = tag

        # we need to split the string into substrings between each pair of
        # (sorted) indices, eg. at index_n and index_n+1. a substring is also needed
        # from the beginning of the string to the first split index, and from
        # the last split index to the end of the string.  
        if len(indexes):
	        l = indexes.keys()
	        l.sort() 
	        first_substring = [(0,l[0])] 
	        last_substring = [(l[-1], len(self.string))]
	        pairs = first_substring + [(l[i], l[i+1]) for i in xrange(len(l)-1)] + last_substring
	        
	        output = []
	        # make sure we don't duplicate any insertions. 
	        already_matched = []
	        for start, stop in pairs:
	            substr = self.string[start:stop]
	            # is there a tag that goes here?
	            if start in indexes.keys() and start not in already_matched:
	                output.append(substr)
	                already_matched.append(start)
	            elif stop in indexes.keys() and stop not in already_matched:
	                output.append(substr)
	                output.append(indexes[stop])
	                already_matched.append(stop)
	            else:
	                output.append(substr)
	        # now join the pieces of the output string back together
	        outputstring = ''.join(output)
	        return outputstring
        else:
            # if there were no matches, return the string unchanged.
            return self.string

class XMLAnnotator(object):
    def __init__(self, string):
        self.regx = Regex(string)

    def register_tag(self, re_string, open_tag, group=None):
        ''' Registers an XML tag to be inserted around a matching regular
        expression. The closing tag is derived from the opening tag. This
        function only registers the tags and their associated regex; apply()
        must be run before the tags are inserted. If group is specified, then
        the the tag is inserted around the matching group instead of the entire
        regular expression. ''' 

        close_tag = self.derive_close_tag(open_tag)
        self.regx.insert_before(re_string, open_tag, group)
        self.regx.insert_after(re_string, close_tag, group)

    def register_tag_start(self, re_string, open_tag, group=None):
        self.regx.insert_before(re_string, open_tag, group)

    def register_tag_close(self, re_string, close_tag, group=None):
        self.regx.insert_after(re_string, close_tag, group)

    def derive_close_tag(self, open_tag):
        space = open_tag.find(' ')
        if space != -1:
            close_tag = open_tag[1:space]
        else:
            close_tag = '</' + open_tag[1:]
        return close_tag

    def apply(self):
        return self.regx.apply()


class CRParser(object):
    ''' Parser functionality and regular expressions common to all
    congressional record documents'''

    re_volume =             r'(?<=Volume )\d+'
    re_number =             r'(?<=Number )\d+'
    re_weekday =            r'Number \d+ \((?P<weekday>[A-Za-z]+)'
    re_month =              r'\([A-Za-z]+, (?P<month>[a-zA-Z]+)'
    re_day =                r'\([A-Za-z]+, [A-Za-z]+ (?P<day>\d{1,2})'
    re_year =               r'\([A-Za-z]+, [A-Za-z]+ \d{1,2}, (?P<year>\d{4})'
    re_chamber =            r'(?<=\[)[A-Za-z]+'
    re_pages =              r'Pages? (?P<pages>[\w\-]+)'
    re_title_start =        r'\S+'
    re_title_end =          r'.+'
    re_newpage = r'\[\[Page \w+\]\]'
    re_underscore = r'\s+_+\s+'

    def spaces_indented(self, theline):
        ''' returns the number of spaces by which the line is indented. '''
        re_textstart = r'\S'
        return re.search(re_textstart, theline).start()
        

class SenateParser(CRParser):
    ''' Parses Senate Documents '''

    # documents with special titles need to be parsed differently than the
    # topic documents, either because they follow a different format or because
    # we derive special information from them. 
    special_titles = {
        "senate" : "" ,
        "Senate" : "" ,
        "prayer" : "",
        "PLEDGE OF ALLEGIANCE" : "",
        "APPOINTMENT OF ACTING PRESIDENT PRO TEMPORE" : "",
        "RECOGNITION OF THE MAJORITY LEADER" : "",
		"SCHEDULE" : "",
        "RESERVATION OF LEADER TIME" : "",
        "MORNING BUSINESS" : "",
        "MESSAGE FROM THE HOUSE" : "",
        "MESSAGES FROM THE HOUSE" : "",
        "MEASURES REFERRED" : "",
        "EXECUTIVE AND OTHER COMMUNICATIONS" : "",
        "SUBMITTED RESOLUTIONS" : "",
        "SENATE RESOLUTION" : "", # this is a special, special title, bc it is a prefix. 
		"SUBMISSION OF CONCURRENT AND SENATE RESOLUTIONS" : "",
		"ADDITIONAL COSPONSORS" : "",
		"ADDITIONAL STATEMENTS" : "",
		"REPORTS OF COMMITTEES" : "", 
		"INTRODUCTION OF BILLS AND JOINT RESOLUTIONS" : "",
		"ADDITIONAL COSPONSORS" : "", 
		"STATEMENTS ON INTRODUCED BILLS AND JOINT RESOLUTIONS" : "", 
		"AUTHORITY FOR COMMITTEES TO MEET" : "", 
		"DISCHARGED NOMINATION" : "", 
		"CONFIRMATIONS" : "", 
		"AMENDMENTS SUBMITTED AND PROPOSED" : "",
		"TEXT OF AMENDMENTS" : "",
		"MEASURES PLACED ON THE CALENDAR" : "",
		"EXECUTIVE CALENDAR" : "",
        "NOTICES OF HEARINGS" : "",
    }

    def __init__(self, fp):
        self.rawlines = fp.readlines()
        self.currentline = 0
        self.date = None
        self.speaker = None
        self.inquote = False
        self.inpara = False
        self.xml = []
        #self.inpreamble = True
        #self.title_begin = False
        #self.intitle = False
        #self.title_end = False

    def parse(self):
        ''' parses a raw senate document and returns the same document marked
        up with XML '''
        print self.rawlines[:15]
        print '\n\n'
        self.markup_preamble()
       
        
    def nextstate(self, statename=None):
        '''knows which state transitions are allowed, and which imply or
        anti-imply which other ones. updates states or throws errors accordingly, and
        generally ensures sanity reigns. if statename = None, then the next
        state is implied. '''
        
        state_transitions = {
            'inpreamble'        :       'intitle',
            'intitle'           :       'topic',
            'topic'             :       'newspeaker', 
        }


    def getstate(self):
        pass

    def markup_preamble(self):
        self.currentline = 1
        theline = self.rawlines[self.currentline]
        annotator = XMLAnnotator(theline)
        annotator.register_tag(self.re_volume, '<volume>')
        annotator.register_tag(self.re_number, '<number>')
        annotator.register_tag(self.re_weekday, '<weekday>', group='weekday')
        annotator.register_tag(self.re_month, '<month>', group='month')
        annotator.register_tag(self.re_day, '<day>', group='day')
        annotator.register_tag(self.re_year, '<year>', group='year')
        xml_line = annotator.apply()
        print xml_line
        self.xml.append(xml_line)
        self.markup_chamber()

    def markup_chamber(self):
        self.currentline = 2
        theline = self.rawlines[self.currentline]
        annotator = XMLAnnotator(theline)
        annotator.register_tag(self.re_chamber, '<chamber>')
        xml_line = annotator.apply()
        print xml_line
        self.xml.append(xml_line)
        self.markup_pages()    
        
    def markup_pages(self):
        self.currentline = 3
        theline = self.rawlines[self.currentline]
        annotator = XMLAnnotator(theline)
        annotator.register_tag(self.re_pages, '<pages>', group='pages')
        xml_line = annotator.apply()
        print xml_line
        self.xml.append(xml_line)
        self.markup_title()

    def clean_line(self, theline):
        ''' strip unwanted parts of documents-- page transitions and spacers.'''
        newpage = re.match(self.re_newpage, theline)
        if newpage:
            theline = theline[:newpage.start()]+theline[newpage.end():]
        underscore = re.match(self.re_underscore, theline)
        if underscore:
            theline = theline[:underscore.start()]+theline[underscore.end():]
        # note: dont strip whitespace when cleaning the lines because
        # whitespace is often the only indicator of the line's purpose or
        # function. 
        return theline

    def get_line(self, offset=0):
        return self.clean_line(self.rawlines[self.currentline+offset])

    def called_to_order(self):
        print 'not yet implemented'
        return

    def no_title(self):
        print 'not yet implemented'
        return

    def parse_special(self):
        print 'not yet implemented'
        return

    def is_special_title(self, title):
        title = title.strip()
        if title in self.special_titles.keys():
            print '{{ title is special }}'
            return True
        if re.match('SENATE RESOLUTION ', title):
            print '{{ title is special }}'
            return True
        else: return False

    def markup_title(self):
        ''' identify and markup the document title. the title is some lines of
        text, usually but not always capitalized, usually but not always
        centered, and followed by a least one empty line. they sometimes have a
        line of dashes separating them from the body of the document. and
        sometimes they don't exist at all.'''

        MIN_TITLE_INDENT = 5

        # skip line 4; it contains a static reference to the GPO website.  
        self.currentline = 5
        theline = self.get_line()
        while not theline.strip():
            self.currentline += 1
            theline = self.get_line()
        
        # we're going to check what kind of title this is once we're done
        # parsing it, so keep track of where it starts. since all the special
        # titles are uniquely specified by their first line, we only need to
        # track that. 
        title_startline = theline

        # if it's not a specially formatted title and it's not indented enough,
        # then it's probably missing a title altogether
        if self.spaces_indented(theline) < MIN_TITLE_INDENT and not self.is_special_title(theline):
            self.no_title()

        else:
            # whew, we made it to a regular old title to parse. 
	        annotator = XMLAnnotator(theline)
	        annotator.register_tag_start(self.re_title_start, '<title>')
	        self.currentline +=1
	        theline = self.get_line()
	
	        # check if the title finished on the sameline it started on:
	        if not theline.strip():
	            annotator.register_tag_close(self.re_title_end, '</title>')
	            xml_line = annotator.apply()
	            print xml_line
	            self.xml.append(xml_line)
	
	        else:
	            # either way we need to apply the tags to the title start. 
	            xml_line = annotator.apply()
	            print xml_line 
	            self.xml.append(xml_line)
	            # now find the title end
	            while theline.strip():
	                self.currentline +=1
	                theline = self.get_line()
	            # once we hit an empty line, we know the end of the *previous* line
	            # is the end of the title. 
	            theline = self.get_line(-1) 
	            annotator = XMLAnnotator(theline)
	            annotator.register_tag_close(self.re_title_end, '</title>')
	            xml_line = annotator.apply()
	            print xml_line
	            self.xml.append(xml_line)
	
        # check for titles with special formatting
        if self.is_special_title(title_startline):
            self.parse_special()

        # the current line after the title should be empty
        print ''
        print self.rawlines[self.currentline:self.currentline+3]

        # check if this is a special title or a regular topic

        # call the appropriate next function

        #self.markup_paragraph()

    def markup_paragraph(self):
        # it's the begining of the paragraph
        
        MIN_LONGQUOTE_INDENT = 7 # ?
        NEW_PARA_INDENT = 2
        # new paragraph?
        # if yes:
        #       is there a new speaker?
        #       is this a recorder comment?
        #       is this the start of a long quote?
        #       is there a shortquote?

        # if shortquote...

        # if longquote...
        
        annotator = XMLAnnotator()
        annotator.register_tag(re_newspeaker)
        # multi-line tags keep track of whether or not the tag has been opened
        # before looking for where it might close. 
        annotator.register_multiline_tag(re_speaking)




if __name__ == '__main__':

    wd = '/tmp/cr/raw/2010/5/12/'
    for file in os.listdir(wd):
        # nothing useful in the front matter. 
        if file.find('FrontMatter') != -1:
            continue
        # skip if it's not a senate file, for now. 
        if file.find('-PgS') == -1:
            continue
        resp = raw_input("process file %s? (y/n/q) " % file)
        if resp == 'n': 
            print 'skipping\n'
        elif resp == 'q':
            sys.exit()
        else:
            # senate documents
            fp = open(os.path.join(wd, file))
            senate = SenateParser(fp)
            senate.parse()


