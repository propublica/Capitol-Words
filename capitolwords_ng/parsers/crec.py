from __future__ import print_function

import logging
from datetime import datetime

import boto3
import re
from lxml import etree
from collections import defaultdict
from collections import Counter

import spacy
import textacy
from textacy.constants import NUMERIC_NE_TYPES
from spacy.parts_of_speech import DET


DEFAULT_XML_NS = {'ns': 'http://www.loc.gov/mods/v3'}


DEFAULT_XPATHS =  {
    'ID': 'string(@ID)',
    'title': 'string(ns:titleInfo/ns:title)',
    'title_part': 'string(ns:titleInfo/ns:partName)',
    'pdf_url': 'string(ns:location/ns:url[@displayLabel="PDF rendition"])',
    'html_url': 'string(ns:location/ns:url[@displayLabel="HTML rendition"])',
    'page_start': 'string(ns:part[@type="article"]/ns:extent/ns:start)',
    'page_end': 'string(ns:part[@type="article"]/ns:extent/ns:end)',
    'speakers': 'ns:name[@type="personal"]/ns:namePart/text()',
}


CREC_BUCKET = 'capitol-words-data'


CREC_PREFIX_TEMPLATE = 'crec/%Y/%m/%d/crec'
CREC_KEY_TEMPLATE = '{prefix}/{id}.htm'

VERB_TAGS = ['BES', 'HVS', 'VB', 'VBD', 'VBN', 'VBP', 'VBZ', 'MD']


def xpath_parse(root, paths, namespaces):
    """Takes an lxml ROOT or element corresponding to the mods.xml doc and
    produces, yanks out useful info, and returns it as a dict.

    PATHS is a dict of fieldname -> xpath query mappings. xpath_parse
    will return records that have the fieldnames with the query
    applied to the root.

    For instance, with PATHS={'foo': '//bar'}, xpath_parse will return
    {'foo': [all instances of bar elements]}.

    """
    results = {}
    for k, p in paths.items():
        value = root.xpath(p, namespaces=namespaces)
        results[k] = value
    return results

def preprocess(text):
    """
    """
    pattern = re.compile('[A-Z!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ ]{10,}')
    index = re.search(pattern, text).start()
    text = text[index:]
    text = re.sub('E\s?X\s?T\s?E\s?N\s?S\s?I\s?O\s?N\s+O\s?F\s+R\s?E\s?M\s?A\s?R\s?K\s?S\n+', '', text)
    text = re.sub('HON\.', 'HON', text)
    text = re.sub('_{3,}', '\n', text)
    text = re.sub('<[^<]+?>', '', text)
    text = re.sub('\n', ' ', text).strip()
    text = re.sub(' {3,}', '. ', text).strip()
    text = re.sub('\s{2,}', ' ', text).strip()
    text = re.sub('\.{2,}', '.', text).strip()
    text = re.sub('\. of', ' of', text)
    text = re.sub('\. in', ' in', text)
    return text

def remove_trailing_tokens(entity, verb=True, adposition=True, conjunction=True, determiner=True,
                           possessive_ending=True):
    """
    Filters a trailing verb and/or conjunction and/or adposition using syntactic part-of-speech tag.
    
    Args:
        entity (:class:`spacy.Span()`)
        verb (bool)
        adposition (bool)
        conjuction (bool)
        determiner (bool)
        possessive_ending (bool)

    Returns:
        str
    """
    # Do not filter verb gerunds (VBG) -- not in VERB_TAGS
    if entity and verb:
        if any(entity[-1].tag_ == v for v in VERB_TAGS):
            entity = entity[:-1]
        # remove trailing verbs like don't and won't as well.
        if entity and len(entity) > 1:
            if entity[-1].tag_ == 'RB' and any(entity[-2].tag_ == v for v in VERB_TAGS):
                entity = entity[:-2]
    if entity and adposition:
        if entity[-1].tag_ == 'IN':
            entity = entity[:-1]
    if entity and conjunction:
        if entity[-1].tag_ == 'CC':
            entity = entity[:-1]
    if entity and determiner:
        if entity[-1].tag_ == 'DT':
            entity = entity[:-1]
    if entity and possessive_ending:
        if entity[-1].tag_ == 'POS':
            entity = entity[:-1]
    if entity:
        return entity
    else:
        return None

def get_named_entities(doc, exclude_types=NUMERIC_NE_TYPES, drop_determiners=True):
    """
    Given a spacy doc, extract named entities and remove unwanted trailing tokens.

    Args:
        doc (:class:`spacy.Doc()`)
        exclude_types (list)
        drop_determiners (bool)

    Returns:
        list of :class:`spacy.Span()`
    """
    named_entities = list(textacy.extract.named_entities(doc, exclude_types=exclude_types,
                                                         drop_determiners=drop_determiners))

    named_entities = [remove_trailing_tokens(ent) for ent in named_entities]
    named_entities = [ne for ne in named_entities if ne is not None]
    return named_entities

def get_named_entity_types(named_entities):
    """
    Given a list of named entities, extract their types.

    Args:
        named_entities (list of :class:`spacy.Span()`)

    Returns:
        dict
    """
    named_entity_types = defaultdict(list)
    for ne in named_entities:
        processed_ne = process_named_entity(ne.text)
        if processed_ne is not None:
            named_entity_types[processed_ne].append(ne.label_)

    for ne in named_entity_types.keys():
        most_common_type = Counter([_type for _type in named_entity_types[ne] if _type]).most_common(1)
        named_entity_types[ne] = most_common_type[0][0] if any(most_common_type) else ''
    return named_entity_types

def get_named_entity_frequencies(named_entities):
    """
    Given a list of named entities, calculate occurrences.

    Args:
        named_entities (list of :class:`spacy.Span()`)

    Returns:
        dict
    """
    processed_nes = []
    for ne in named_entities:
        processed_ne = process_named_entity(ne.text)
        if processed_ne is not None:
            processed_nes.append(processed_ne)

    named_entity_frequencies = Counter(processed_nes)
    return named_entity_frequencies

def process_named_entity(named_entity, marks='!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~'):
    """
    Processes named entity by removing punctuations and at the end camel cases it.

    Args:
        named_entity (str)
        marks (str)

    Returns:
        str
    """
    # TODO. replace the line below with commented line after textacy incorporates marks
    # named_entity = textacy.preprocess.remove_punct(named_entity, marks=marks)
    named_entity = remove_punct(named_entity, marks=marks)
    named_entity = camel_case(named_entity)

    return named_entity if named_entity else None

def remove_punct(text, marks=None):
    """
    Remove punctuation from ``text`` by replacing all instances of ``marks``
    with an empty string.
    Args:
        text (str): raw text
        marks (str): If specified, remove only the characters in this string,
            e.g. ``marks=',;:'`` removes commas, semi-colons, and colons.
            Otherwise, all punctuation marks are removed.
    Returns:
        str
    """
    if marks:
        return re.sub('[{}]+'.format(re.escape(marks)), '', text, flags=re.UNICODE)
    else:
        if isinstance(text, unicode_):
            return text.translate(PUNCT_TRANSLATE_UNICODE)
        else:
            return text.translate(None, PUNCT_TRANSLATE_BYTES)

def get_noun_chunks(doc, exclude_types=NUMERIC_NE_TYPES, drop_determiners=True):
    """
    Extract ordered list of noun chunks from a spacy-parsed doc,
    optionally filtering by the entity types and frequencies.
    
    Args:
        doc (:class:`spacy.Doc()`)
        exclude_types (list)
        drop_determiners (bool)
    
    Returns:
        list of :class:`spacy.Span()`
    """
    noun_chunks = doc.noun_chunks
    if any(exclude_types):
        noun_chunks = [
            nc for nc in noun_chunks
            if not any([n.ent_type_ in exclude_types for n in nc])
        ]
    if drop_determiners:
        noun_chunks = [nc if nc[0].pos != DET else nc[1:] for nc in noun_chunks]

    return list(noun_chunks)

def camel_case(entity, force=False):
    """
    Camel-cases all words in entity except when a word is all capital letters.
    
    Args:
        entity (str)
        force (bool)
    
    Returns:
        str
    """
    _entity = str(entity)
    if force:
        _entity = " ".join([w.title() if w.isupper() else w for w in _entity.split()])
    else:
        _entity = " ".join([w.title() if not w.isupper() else w for w in _entity.split()])
    return unicode(_entity)


class CRECParser(object):

    def __init__(self, bucket='capitol-words-data', xml_namespace=None, xpaths=DEFAULT_XPATHS):
        if xml_namespace is None:
            self.xml_namespace = DEFAULT_XML_NS
        else:
            self.xml_namespace = xml_namespace
        self.xpaths = xpaths
        self.s3 = boto3.client('s3')
        self.bucket = bucket
        self.nlp = spacy.load('en')

    def parse_mods_file(self, mods_file):
        doc = etree.parse(mods_file)
        constituents = doc.xpath(
            '//ns:relatedItem[@type="constituent"]',
            namespaces=DEFAULT_XML_NS,
        )
        records = [
            xpath_parse(r, self.xpaths, namespaces=self.xml_namespace)
            for r in constituents
        ]
        date_issued_str = doc.xpath(
            'string(//ns:originInfo/ns:dateIssued)',
            namespaces=DEFAULT_XML_NS,
        )
        date_issued = datetime.strptime(date_issued_str, '%Y-%m-%d')
        prefix = date_issued.strftime(CREC_PREFIX_TEMPLATE)
        for record in records:
            record['date_issued'] = date_issued
            s3_key = CREC_KEY_TEMPLATE.format(
                prefix=prefix,
                id=record['ID'].strip('id-')
            )
            failed_retrievals = []
            try:
                response = self.s3.get_object(Bucket=self.bucket, Key=s3_key)
                record['content'] = response['Body'].read()
            except Exception as e:
                failed_retrievals.append(s3_key)

        if len(failed_retrievals) > 0:
            logging.error(
                'Failed to rerieve {0}/{1} crec docs.'.format(
                    len(failed_retrievals), len(records)
                )
            )
            for s3_key in failed_retrievals:
                logging.error('Failed retrieval: "{0}".'.format(s3_key))
        else:
            logging.info('All crec retrievals succeeded.')

        for record in records:
            record['named_entities'] = None
            record['noun_chunks'] = None    
            if (record['ID'].split('-')[-1].startswith('PgD') or
                record['ID'].split('-')[-2].startswith('PgD') or
                record['content'] is None or
                'content' not in record.keys()):
                # dont process daily digests
                continue

            text = preprocess(record['content'])            
            textacy_text = textacy.Doc(self.nlp(unicode(text)))
            named_entities = get_named_entities(textacy_text)
            if any(named_entities):
                named_entity_types = get_named_entity_types(named_entities)
                named_entity_freqs = get_named_entity_frequencies(named_entities)
                record['named_entities'] = [
                    ('|'.join([ne, named_entity_types[ne]]), named_entity_freqs[ne])
                    for ne in sorted(named_entity_freqs, key=named_entity_freqs.get, reverse=True)]

            phrases = get_noun_chunks(textacy_text.spacy_doc)
            # Filter noun chunks

        return records
