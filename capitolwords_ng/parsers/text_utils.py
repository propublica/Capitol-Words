from __future__ import print_function

import logging

from collections import defaultdict
from collections import Counter

import textacy
from textacy.constants import NUMERIC_NE_TYPES
from spacy.parts_of_speech import DET

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
    named_entities = [ne for ne in named_entities if ne is not None and len(ne.text) > 1]
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

def process_named_entity(named_entity, marks='!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~',
                         beginning_marks='!"#$%&\'()*+,-/.:;<=>?@[\\]^_`{|}~ ',
                         trailing_marks=None):
    """
    Processes named entity by removing punctuations and at the end camel cases it.

    Args:
        named_entity (str)
        marks (str)
        beginning_marks (str)

    Returns:
        str
    """
    # TODO. replace the line below with commented line after textacy incorporates marks
    # named_entity = textacy.preprocess.remove_punct(named_entity, marks=marks)
    named_entity = remove_punct(named_entity, marks=marks, beginning_marks=beginning_marks)
    named_entity = camel_case(named_entity)

    return named_entity if named_entity else None

def remove_punct(text, marks=None, beginning_marks=None, trailing_marks=None):
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
    return _entity