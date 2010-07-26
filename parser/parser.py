#!/usr/bin/python

''' Parse the plain text version of congressional record documents and mark them up with xml.'''

import re, datetime, os

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
        l = indexes.keys()
        l.sort() 
        first_substring = [(0,l[0])] 
        last_substring = [(l[-1], len(self.string))]
        pairs = first_substring + [(l[i], l[i+1]) for i in xrange(len(l)-1)] + last_substring
        print pairs
        print ''
        
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
#           print 'output is now:'
#           print output
        # now join the pieces of the output string back together
        outputstring = ''.join(output)
        return outputstring

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

    def derive_close_tag(self, open_tag):
        space = open_tag.find(' ')
        if space != -1:
            close_tag = open_tag[1:space]
        else:
            close_tag = '</' + open_tag[1:]
        return close_tag

    def apply(self):
        return self.regx.apply()


class SenateParser(object):
    re_volume =     r'(?<=Volume )\d+'
    re_number =     r'(?<=Number )\d+'
    re_weekday =    r'Number \d+ \((?P<weekday>[A-Za-z]+)'
    re_month =      r'\([A-Za-z], (?P=<month>[a-zA-Z]+)'
#    re_day =        r'(?<=\([A-Za-z], [a-zA-Z]+ )\d{1,2}'
#    re_year =       r'(?<=\([A-Za-z], [a-zA-Z]+ \d{1,2}, )\d{4}'

    def __init__(self, fp):
        self.rawlines = fp.readlines()
        self.currentline = 0
        self.date = None
        self.speaker = None
        self.inquote = False
        self.inpara = False
        self.xml = []

    def parse(self):
        ''' parses a raw senate document and returns the same document marked up with XML '''

        # preable text is always in the same place and same format. 
        self.markup_preamble()
        self.markup_title()
        
    def markup_preamble(self):
        theline = self.rawlines[1]
        annotator = XMLAnnotator(theline)
        annotator.register_tag(self.re_volume, '<volume>')
        annotator.register_tag(self.re_number, '<number>')
        annotator.register_tag(self.re_weekday, '<weekday>', group='weekday')

        xml_line = annotator.apply()
        print xml_line
        self.xml.append(xml_line)
        return

    def markup_title(self):
        pass

if __name__ == '__main__':

    wd = '/tmp/cr/raw/2010/5/12/'
    for file in os.listdir(wd):
        resp = raw_input("process file %s? (y/n) " % file)
        if resp == 'y':
            fp = open(os.path.join(wd, file))
            senate = SenateParser(fp)
            senate.parse()
        else: print 'skipping\n'



