from __future__ import print_function

import logging

from collections import defaultdict
from collections import Counter
import re
import sys
import unicodedata

import textacy
from textacy.compat import unicode_
from textacy.constants import NUMERIC_NE_TYPES, PUNCT_TRANSLATE_UNICODE, PUNCT_TRANSLATE_BYTES
from spacy.parts_of_speech import DET


VERB_TAGS = ['BES', 'HVS', 'VB', 'VBD', 'VBN', 'VBP', 'VBZ', 'MD']

ENTITY_BLACKLIST = ['Hon', 'Jr', 'Memory', 'Speaker', 'Thereupon', 'Sr', 'Tribute To Dr', 'REP',
                    'HON', 'JR', 'SR', 'Madam', 'Dear Madam', 'Sincerely', 'Speaker Pro Tempore',
                    'Adjournment']

ENTITY_TRAILING_BLACKLIST = (' On', ' Sine Die Adjournment')

NOUN_CHUNK_BLACKLIST = [' hon ',  'sine die adjournment', 'who', 'where', 'when', 'what',
                        'behalf', 'somebody', 'some one', 'anybody', 'any one']

NOUN_CHUNK_LEMMA_BLACKLIST = ['-PRON-']

CHAR_COUNT_THRESHOLD = 4

def preprocess(text):
    """
    Preprocess crec text file to filter out html tags and suprfluous parts!

    Args:
        text (str)

    Returns:
        str
    """
    pattern = re.compile('[A-Z!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ ]{10,}')
    index = re.search(pattern, text).start()
    text = text[index:]
    text = re.sub('E\s?X\s?T\s?E\s?N\s?S\s?I\s?O\s?N\s+O\s?F\s+R\s?E\s?M\s?A\s?R\s?K\s?S\n+', '', text)
    text = re.sub('HON\.', 'HON', text)
    text = re.sub('\n{2,}', '. ', text)
    text = re.sub('_{3,}', '\n', text)
    text = re.sub('<[^<]+?>', '', text)
    text = re.sub('\n{3,}', '. ', text).strip()
    text = re.sub('\n', ' ', text).strip()
    text = re.sub(' {3,}', ' ', text).strip()
    text = re.sub('\s{2,}', ' ', text).strip()
    text = re.sub('\.{2,}', '.', text).strip()
    text = re.sub('[\. \. ]{2,}', '. ', text).strip()
    text = re.sub('[\. \.]{2,}', '. ', text).strip()
    text = re.sub('\. of', ' of', text)
    text = re.sub('\. in', ' in', text)
    return text

def remove_trailing_tokens(entity, verb=True, adposition=True, conjunction=True, determiner=True,
                           possessive_ending=True):
    """
    Filters a trailing verb, conjunction, adposition, determiner and/or possessive tags using
    syntactic part-of-speech tag.
    
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
                logging.debug('Removing trailing verb from named entity: %s', entity)
                entity = entity[:-2]
    if entity and adposition:
        if entity[-1].tag_ == 'IN':
            logging.debug('Removing trailing conjunction from named entity: %s', entity)
            entity = entity[:-1]
    if entity and conjunction:
        if entity[-1].tag_ == 'CC':
            logging.debug('Removing trailing conjunction from named entity: %s', entity)
            entity = entity[:-1]
    if entity and determiner:
        if entity[-1].tag_ == 'DT':
            logging.debug('Removing determiner from named entity: %s', entity)
            entity = entity[:-1]
    if entity and possessive_ending:
        if entity[-1].tag_ == 'POS':
            logging.debug('Removing possessive ending from named entity: %s', entity)
            entity = entity[:-1]
    if entity:
        return entity
    else:
        return None


def remove_punct(text, marks=None, beginning_marks=None, trailing_marks=None):
    """
    Remove punctuation from ``text`` by replacing all instances of ``marks``,
    ``beginning_marks`` or ``trailing_marks`` with an empty string.
    Args:
        text (str): raw text
        marks (str): If specified, remove only the characters in this string,
            e.g. ``marks=',;:'`` removes commas, semi-colons, and colons.
        beginning_marks (str): If specified, remove only the characters in this
            string from the beginning of the text, e.g. ``marks='^'`` removes
            ``^`` from the beginning of text.
        trailing_marks (str): If specified, remove only the characters in this
            string from the end of the text, e.g. ``marks='%'`` removes ``%``
            from the beginning of text. If non the above is given, all punctuation
            marks are removed.
    Returns:
        str
    """
    # First off, replace dashes with white space: import-export banks --> import export banks
    text = re.sub('-', ' ', text, flags=re.UNICODE)
    text = re.sub('  ', ' ', text, flags=re.UNICODE).strip()
    if beginning_marks:
        text = re.sub('^[{}]+'.format(re.escape(beginning_marks)), '', text, flags=re.UNICODE)
    if trailing_marks:
        text = re.sub('$[{}]+'.format(re.escape(trailing_marks)), '', text, flags=re.UNICODE)
    if marks:
        return re.sub('[{}]+'.format(re.escape(marks)), '', text, flags=re.UNICODE)
    else:
        if isinstance(text, unicode_):
            return text.translate(PUNCT_TRANSLATE_UNICODE)
        else:
            return text.translate(None, PUNCT_TRANSLATE_BYTES)


def camel_case(entity, force=False, threshold=CHAR_COUNT_THRESHOLD):
    """
    Camel-cases all words in entity except when a word is all capital letters.
    
    Args:
        entity (str)
        force (bool)
        threshold (int)
    
    Returns:
        str
    """
    _entity = str(entity)
    if force:
        if len(_entity.split()) > 1:
            _entity = " ".join([w.title() for w in _entity.split()])
        else:
            # If a word is shorter than `threshold` characters and all caps, it is
            # not titled. This lets us preserve all caps for words like `WBUR` or `NPR`.
            _entity = _entity.title() if len(_entity) > threshold else _entity
    else:
        _entity = " ".join([w.title() if not w.isupper() else w
                            for w in _entity.split()])
    return _entity

def get_named_entities(doc, exclude_types=NUMERIC_NE_TYPES, drop_determiners=True):
    """
    Given a spacy doc, extract named entities and remove unwanted trailing tokens.

    Args:
        doc (:class:`spacy.Doc()`)
        exclude_types (list)
        drop_determiners (bool)

    Returns:
        list of tuple (:class:`spacy.Span()`, str)
    """
    named_entities = list(textacy.extract.named_entities(doc, exclude_types=exclude_types,
                                                         drop_determiners=drop_determiners))

    named_entities = [remove_trailing_tokens(ent) for ent in named_entities]
    named_entities = [ne for ne in named_entities if ne is not None and len(ne.text) > 1]
    processed_named_entities = process_named_entity(named_entities)

    return processed_named_entities

def process_named_entity(named_entities, marks='!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~',
                         beginning_marks='!"#$%&\'()*+,-/.:;<=>?@[\\]^_`{|}~ ',
                         trailing_marks=None):
    """
    Processes named entity by removing punctuations & black list entities and camel cases it.

    Args:
        named_entities (list of :class:`spacy.Doc()`)
        marks (str)
        beginning_marks (str)
        trailing_marks (str)

    Returns:
        str
    """
    processed_named_entities = []
    for named_entity in named_entities:
        ne = named_entity.text
        # TODO. replace the line below with the commented line after textacy incorporates marks
        # named_entity = textacy.preprocess.remove_punct(named_entity, marks=marks)
        ne = remove_punct(ne, marks=marks, beginning_marks=beginning_marks)
        ne = camel_case(ne, force=True)
        if ne is not None and ne.title() not in ENTITY_BLACKLIST:
            if ne.endswith(ENTITY_TRAILING_BLACKLIST):
                # For sentences that look like `IN HONOR OF JEIRAN ON HIS 100TH BIRTHDAY`,
                # named entity is `JEIRAN ON` as `ON` is ascribed the wrong NNP pos tag instead
                # of CC pos tag, so we need to manually strip the extra `ON`. All caps sentences
                # are tough to parse.
                logging.info('Removing trailing blacklisted tokens from entity: %s', ne)
                pattern = r' ' + '|'.join([i + '$' for i in ENTITY_TRAILING_BLACKLIST])
                ne = re.split(pattern, ne)[0]
            processed_named_entities.append((named_entity, ne))
    
    return processed_named_entities

def get_named_entity_types(named_entities):
    """
    Given a list of named entities, extract their types. If one named entity is attributed
    different types, pick the most common type. Existing named entity types are listed here:
    https://spacy.io/docs/usage/entity-recognition#entity-types

    Args:
        named_entities (list of tuple of (:class:`spacy.Span()`, str))

    Returns:
        dict
    """
    named_entity_types = defaultdict(list)
    for ne, processed_ne in named_entities:
        if processed_ne is not None:
            named_entity_types[processed_ne].append(ne.label_)

    # Determine the most common entity type per entity and go with that.
    for ne in named_entity_types.keys():
        most_common_type = Counter(
            [_type for _type in named_entity_types[ne] if _type]).most_common(1)
        named_entity_types[ne] = most_common_type[0][0] if any(most_common_type) else ''

    # Reverse the mapping to {named_entity_type: named_entity}
    named_entity_types_ = defaultdict(list)
    for ne, _type in named_entity_types.items():
        named_entity_types_[_type].append(ne)

    return named_entity_types_

def get_named_entity_frequencies(named_entities):
    """
    Given a list of named entities, calculate occurrences.

    Args:
        named_entities (list of tuple of (:class:`spacy.Span()`, str))

    Returns:
        dict
    """
    processed_nes = []
    for _, processed_ne in named_entities:
        if processed_ne is not None:
            processed_nes.append(processed_ne)

    named_entity_frequencies = Counter(processed_nes)
    return named_entity_frequencies

def get_noun_chunks(doc, drop_determiners=True):
    """
    Extract ordered list of noun chunks from a spacy doc and optionally filter by the types.
    
    Args:
        doc (:class:`spacy.Doc()`)
        drop_determiners (bool)
    
    Returns:
        list
    """
    noun_chunks = [nc for nc
                   in textacy.extract.noun_chunks(doc, drop_determiners=drop_determiners)]

    # Filter blacklisted words and drop noun chunks that include pronouns (these are too specific)
    processed_noun_chunks = []
    for nc in noun_chunks:
        is_blacklisted = any(b in nc.text.lower() for b in NOUN_CHUNK_BLACKLIST) or \
                         any(b in nc.lemma_ for b in NOUN_CHUNK_LEMMA_BLACKLIST)
        if not is_blacklisted:
            nc = remove_punct(nc.text, marks='!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~')
            processed_noun_chunks.append(nc.title())
        else:
            # logging.info('Removing blacklisted noun chunks: %s', nc)
            pass

    return processed_noun_chunks

def named_entity_dedupe(noun_chunks, named_entities):
    """
    Some of the noun chunks are naturally named entities. Exclude these from the noun chunks.

    Args:
        noun_chunks (list)
        named_entities (list)

    Returns:
        list
    """
    noun_chunks_ = {nc.lower() for nc in noun_chunks}
    named_entities_ = {ne.lower() for ne in named_entities}
    deduped_uniques = noun_chunks_ - named_entities_
    noun_chunks_ = [nc for nc in noun_chunks_ if nc in deduped_uniques]
    return noun_chunks_
    