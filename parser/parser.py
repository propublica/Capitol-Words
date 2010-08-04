#!/usr/bin/python

''' Parse the plain text version of congressional record documents and mark them up with xml.'''

import re, datetime, os, sys

DEBUG = False

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

    def register_tag_open(self, re_string, open_tag, group=None):
        self.regx.insert_before(re_string, open_tag, group)

    def register_tag_close(self, re_string, close_tag, group=None):
        self.regx.insert_after(re_string, close_tag, group)

    def derive_close_tag(self, open_tag):
        space = open_tag.find(' ')
        if space != -1:
            close_tag = '</' + open_tag[1:space] + '>'
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
    re_newpage =            r'\[\[Page \w+\]\]'
    re_underscore =         r'\s+_+\s+'
    # a new speaker might either be a legislator's name, or a reference to the role of president of presiding officer. 
    re_newspeaker =         r'^  (?P<name>(((Mr)|(Ms)|(Mrs))\. [A-Z \-]+(of [A-Z][a-z]+)?)|(The (ACTING )?PRESIDENT pro tempore)|(The PRESIDING OFFICER))\.'

    # whatever follows the statement of a new speaker marks someone starting to
    # speak. if it's a new paragraph and there's already a current_speaker,
    # then this re is also used to insert the <speaking> tag. 
    re_speaking =           r'^  (((((Mr)|(Ms)|(Mrs))\. [A-Z \-]+(of [A-Z][a-z]+)?)|(The (ACTING )?PRESIDENT pro tempore)|(The PRESIDING OFFICER))\. )?(?P<start>.)'
    re_startshortquote =    r'``'
    re_endshortquote =      r"''"
    re_longquotestart =    r' {7,}\w'
    re_endofline =          r'$'
    re_recorderstart =      (r'(The assistant legislative clerk read as follows)'
                             + '|(The nomination considered and confirmed is as follows)'
                             + ''
                            )
    re_recorderend =        re_recorderstart # for now

    def spaces_indented(self, theline):
        ''' returns the number of spaces by which the line is indented. '''
        re_textstart = r'\S'
        return re.search(re_textstart, theline).start()
        
class HouseParser(CRParser):
    pass

class ExtensionsParser(CRParser):
    pass

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
        "REPORTS OF COMMITTEES DURING ADJOURNMENT" : "",
    }

    def __init__(self, abspath):
        self.filename = abspath
        fp = open(document)
        self.rawlines = fp.readlines()
        self.currentline = 0
        self.date = None
        self.current_speaker = None
        self.inquote = False
        self.new_paragraph = False
        self.recorder = False
        self.inlongquote = False
        self.xml = []

    def parse(self):
        ''' parses a raw senate document and returns the same document marked
        up with XML '''
        print self.rawlines[:15]
        print '\n\n'
        self.markup_preamble()
       
        
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
        if self.currentline+offset > len(self.rawlines)-1:
            return None
        return self.clean_line(self.rawlines[self.currentline+offset])

    def called_to_order(self):
        print 'not yet implemented'
        return

    def no_title(self):
        print 'not yet implemented'
        # one of the things to do here is when the acting president is assigned
        # for the day, make note of who they are so we can assign words spoken
        # by that role to the correct legislator 
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
            annotator.register_tag_open(self.re_title_start, '<title>')
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
            else:
                self.markup_paragraph()
	
            # note that as we exit this function, the current line is one PAST
            # the end of the title, which should generally be a blank line. 

    def set_speaker(self, theline):
        # checks if there is a new speaker, and if so, set the current_speaker
        # attribute, and returns the name of the new (and now current) speaker.
        # else leaves the current speaker.  
        new_speaker = re.search(self.re_newspeaker, theline)
        if new_speaker:
            name = new_speaker.group('name')
            self.current_speaker = name # XXX TODO this should be a unique ID
        return self.current_speaker

    def markup_paragraph(self):
        ''' this is the standard paragraph parser. handles new speakers,
        standard recorder comments, long and short quotes, etc. '''
        
        MIN_LONGQUOTE_INDENT = 7 # ?

        # get to the first line 
        theline = self.get_line()
        while not theline.strip():
            self.currentline += 1
            theline = self.get_line()

        while theline:
            self.preprocess_state(theline)
            annotator = XMLAnnotator(theline)
            # some things only appear on the first line of a paragraph
            if self.new_paragraph:
                annotator.register_tag_open(self.re_recorderstart, '<recorder>')
                annotator.register_tag(self.re_newspeaker, '<speaker name="%s">' % self.current_speaker, group='name')
                if not self.recorder:
                    annotator.register_tag_open(self.re_speaking, '<speaking name="%s">' % self.current_speaker, group='start')
            # some things can appear on any line of a paragraph:
            annotator.register_tag_open(self.re_startshortquote, '<quote speaker="%s">' % self.current_speaker)
            # XXX TODO--> insert long quote start and end detection here. 
            
            if self.inquote:
                annotator.register_tag_close(self.re_endshortquote, '</quote>')

            if self.paragraph_ends():
                if self.recorder:
                    annotator.register_tag_close(self.re_endofline, '</recorder>')
                elif self.inlongquote:
                    annotator.register_tag_close(self.re_endofline, '</quote>')
                else:
                    annotator.register_tag_close(self.re_endofline, '</speaking>')

            xml_line = annotator.apply()
            print xml_line
            self.xml.append(xml_line)

            # do some post processing
            self.postprocess_state(theline)

            # get the next line and do it all again
            self.currentline +=1
            theline = self.get_line()
            while theline and not theline.strip():
                self.currentline += 1
                theline = self.get_line()
            if not theline:
                # end of file
                print ''.join(self.xml)
                return

    def preprocess_state(self, theline):
        ''' in certain cases we need to match a regular expression AND a state,
        so do some analysis to determine which tags to register. '''

        if self.is_new_paragraph(theline):
            self.new_paragraph = True

            # check if this is a subheading...
            # if re.search(self.re_subheading, theline):
            # set speaker to None
            #   pass
            
            # in the case of a long quote, we don't change the current speaker. 
            if re.search(self.re_longquotestart, theline):
                self.inlongquote = True
            else: 
                # if it's a recorder reading, then make a note that they are
                # the speaker 
                if re.search(self.re_recorderstart, theline):
                    self.recorder = True
                    self.currentspeaker = None #'Recorder'
                else:
                    self.set_speaker(theline)

        else:
            self.new_paragraph = False

        # if a quote starts we are "in a quote" but we stay in that quote until
        # we detect it ends. 
        if re.search(self.re_startshortquote, theline):
            self.inquote = True

        # debugging..
        print 'new paragraph? %s' % self.new_paragraph
        if self.current_speaker:
            print 'current speaker: ' + self.current_speaker 
        else:
            print 'no current speaker'
        print 'in long quote? %s' % self.recorder
        print 'in recorder? %s' % self.recorder
        print 'in quote? %s' % self.inquote

    def postprocess_state(self, theline):
        ''' in certain cases where a state ends on a line, we only want to note
        that after the proper tags have been registered and inserted. ''' 
        
        if not self.recorder and not self.current_speaker:
            # this is a wierd state we shouldn't be in
            print '!! unrecognized state. exiting.'
            print self.rawlines
            sys.exit()
            #show_errors_and_exit()

        if self.inquote and re.search(self.re_endshortquote, theline):
            self.inquote = False

        if self.recorder and re.search(self.re_recorderend, theline):
            self.recorder = False

        if self.inlongquote and self.paragraph_ends():
            self.inlongquote = False

    def paragraph_ends(self):
        ''' check if the current paragraph ends by looking ahead to what the
        next non-empty line is. idempotent. '''

        # a paragraph ending is really only indicated by the formatting which
        # follows it. if a line is followed by a new paragraph, a long section
        # of quoted text, or a subheading, then we know this must be the end of
        # athe current paragraph. all of those possibilities are indicated by
        # the indentation level.  

        offset = 1
        theline = self.get_line(offset)
        while theline and not theline.strip():
            offset += 1
            theline = self.get_line(offset)
    
        # if the document ends here, then it's certainly also the end of the
        # paragraph
        if not theline:
            return True
        # new para or new long quote?
        if self.is_new_paragraph(theline):
            return True
        return False

    def is_new_paragraph(self, theline):
        NEW_PARA_INDENT = 2
        if self.spaces_indented(theline) >= NEW_PARA_INDENT:
            return True
        else:
            return False

def usage():
    print 'Usage:'
    print 'You must pass in a congressional record filename, or specify yyyy/mm/dd [chamber],'
    print 'where chamber is one of [senate|house|extensions]. eg:'
    print './parser.py CREC-2010-07-12-pt1-PgS5744-2.txt'
    print './parser.py 2010/07/02 senate'
    print ''
    sys.exit()

if __name__ == '__main__':

    # processes a file or entire directory
    
    wd = '/tmp/cr/raw'
    parsers = {
        'senate':       SenateParser,
        'house' :       HouseParser,
        'extensions' :  ExtensionsParser,
        'S':            SenateParser,
        'H' :           HouseParser,
        'E' :           ExtensionsParser,
     }

    chambers = {
        'senate':       '-PgS',
        'house' :       '-PgH',
        'extensions' :  '-PgE',
        'S':            '-PgS',
        'H' :           '-PgH',
        'E' :           '-PgE',
    }

    if len(sys.argv) < 2:
        usage()

    if sys.argv[1].endswith('.txt'):
        file = sys.argv[1]
        if file.startswith('/'):
            print 'opening file %s' % file
            abspath = file
        else:
            # get date from filename
            parts = file.split('-')
            year = parts[1]
            month = parts[2]
            day = parts[3]
            abspath = os.path.join(wd, '%s/%s/%s/%s' % (year, month, day, file))
            print 'processing file %s' % path
        chamber = re.search(r'-Pg(?P<chamber>E|S|H)', abspath).group('chamber')
        chamber_doc = parsers[chamber](abspath)
        chamber_doc.parse()


    else:
        directory = sys.argv[1]
        path = os.path.join(wd, directory)
        print path
        chamber = sys.argv[2].lower()
        correct_chamber = chambers[chamber]

        if not os.path.exists(path):
            print 'no records exist for that date. try a different date.'
            usage()

        for file in os.listdir(path):
            # nothing useful in the front matter. 
            if file.find('FrontMatter') != -1 or file.find(correct_chamber) == -1:
                continue
            resp = raw_input("process file %s? (y/n/q) " % file)
            if resp == 'n': 
                print 'skipping\n'
            elif resp == 'q':
                sys.exit()
            else:
                abspath = os.path.join(path, file)
                chamber_doc = parsers[chamber](abspath)
                chamber_doc.parse()


