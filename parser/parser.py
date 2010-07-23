#!/usr/bin/python

''' Parse the plain text version of congressional record documents and mark them up with xml.'''

# date
# speaker
# bill number
# 

import re, datetime, os


class Regex(object):

    def __init__(self, string):
        self.string = string
        # a list of tuples containing (regex_string, xml_opening_tag)
        self.opentags = []
        self.closetags = []

    def insert_before(self, re_string, tag):
        # start tags are inserted at the start of a regex match
        self.opentags.append((re_string, tag))
    
    def insert_after(self, re_string, tag):
        # start tags are inserted at the start of a regex match
        self.closetags.append((re_string, tag))


    def apply(self):
        indexes = {}
        # identify where all the opening tags go (those that get inserted at
        # the start of the regex match)
        for regex, tag in self.opentags:
            matchobj = re.search(regex, self.string)
            if matchobj:
                start = matchobj.start()
                indexes[start] = tag
        # identify where all the closing tags go (those that get inserted at
        # the end of the regex match)
        for regex, tag in self.closetags:
            matchobj = re.search(regex, self.string)
            if matchobj:
                end = matchobj.end()
                indexes[end] = tag
        print indexes
        print ''

        # we need to split the string into substrings between each pair of
        # sorted indices, eg. at index_n and index_n+1. a substring is also needed
        # from the beginning of the string to the first split index, and from
        # the last split index to the end of the string.  
        l = indexes.keys()
        l.sort() 
        first_substring = [(0,l[0])] 
        last_substring = [(l[-1], len(self.string))]
        pairs = first_substring + [(l[i], l[i+1]) for i in xrange(len(l)-1)] + last_substring
        print pairs
        print ''
        
        # make sure we don't duplicate any xml insertions. 
        already_matched = []
        
        xml = []
        for start, stop in pairs:
            print start, stop
            substr = self.string[start:stop]
            # is there a tag that goes here?
            if start in indexes.keys() and start not in already_matched:
                print 'adding start'
                xml.append(indexes[start])
                xml.append(substr)
                already_matched.append(start)
            elif stop in indexes.keys() and stop not in already_matched:
                print 'adding stop'
                print stop
                print indexes[stop]
                xml.append(substr)
                xml.append(indexes[stop])
                already_matched.append(stop)
            else:
                xml.append(substr)
                print 'nothing was added'
            print 'xml is now:'
            print xml
        # now join the pieces of the xml string back together
        xmlstring = ''.join(xml)
        return xmlstring

class XMLAnnotator(object):
    def __init__(self, string):
        self.regx = Regex(string)

    def register_tag(self, re_string, open_tag):
        close_tag = self.derive_close_tag(open_tag)
        self.regx.insert_before(re_string, open_tag)
        self.regx.insert_after(re_string, close_tag)

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
    def __init__(self, fp):
        self.rawlines = fp.readlines()
        self.currentline = 0
        self.date = None
        self.speaker = None
        self.inquote = False
        self.inpara = False
        self.xml = ""

    def parse(self):
        ''' parses a raw senate document and returns the same document marked up with XML '''

        # preable text is always in the same place and same format. 
        self.markup_volume()
        self.markup_number()
        self.markup_date()
        self.markup_chamber()
        self.markup_pages()
        self.markup_title()
        

if __name__ == '__main__':
    line = '[Congressional Record Volume 156, Number 95 (Wednesday, June 23, 2010)]'
    regx = Regex(line)
    re_volume = r'(?<=Volume )\d+'
    re_number = r'(?<=Number )\d+'
    re_weekday = r'(?<=Number \d+ \()[A-Za-z]+'
    re_month = ''
    re_day = ''
    re_year = ''
    regx.insert_before(re_volume, '<volume>')
    regx.insert_after(re_volume, '</volume>')
    regx.insert_before(re_number, '<number>')
    regx.insert_after(re_number, '</number>')
    xml = regx.apply()
    print 'result was:'
    print xml

