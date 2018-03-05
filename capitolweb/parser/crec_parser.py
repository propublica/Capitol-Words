from __future__ import print_function

import logging
import re
from datetime import datetime
from collections import Counter
from itertools import chain
import json

import boto3
import spacy
import textacy
from lxml import etree
from fuzzywuzzy import process
from django.utils.functional import cached_property
from django.conf import settings

from botocore.exceptions import ClientError

from cwapi.models import SpeakerWordCounts
from cwapi.es_docs import CRECDoc
# from cwapi.es_docs import AttributedSegmentDoc
import parser.text_utils as text_utils
from scraper.crec_scraper import crec_s3_key


logger = logging.getLogger(__name__)


DEFAULT_XML_NS = {'ns': 'http://www.loc.gov/mods/v3'}


SPACY_NLP = spacy.load('en')


APPROX_MATCH_THRESHOLD = 90


HOUSE_GENERIC_SPEAKERS = [
    'The CLERK', 'The Acting CLERK', 'The ACTING CLERK',
    'The SPEAKER pro tempore', 'The SPEAKER'
    'The Acting SPEAKER pro tempore', 'The ACTING SPEAKER pro tempore',
    'The Acting CHAIR', 'The ACTING CHAIR', 'The Acting CHAIRMAN',
    'The ACTING CHAIRMAN', 'The CHAIRMAN', 'The CHAIRWOMAN',
]


SENATE_GENERIC_SPEAKERS = [
    'The PRESIDING OFFICER', 'The PRESIDENT pro tempore',
    'The Acting PRESIDENT pro tempore', 'The ACTING PRESIDENT pro tempore',
    'The VICE PRESIDENT', 'The CHIEF JUSTICE', 'Mr. Counsel', 'Mrs. Counsel',
    'Ms. Counsel'
]


GENERIC_SPEAKERS = HOUSE_GENERIC_SPEAKERS + SENATE_GENERIC_SPEAKERS


class CRECParser(object):

    def __init__(self,
                 xml_tree,
                 date_issued,
                 xml_namespace=DEFAULT_XML_NS):
        self._xml_tree = xml_tree
        self._xml_namespace = xml_namespace
        self.date_issued = date_issued
        self.s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    def _get_by_xpath(self, xml_tree, xpath):
        return xml_tree.xpath(xpath, namespaces=self._xml_namespace)

    @cached_property
    def id(self):
        """@ID field in mods metadata, usually corresponds to filename minus the
        file extension.

        Example:
            "id-CREC-2017-01-20-pt1-PgD55"
        """
        return self._get_by_xpath(self._xml_tree, 'string(@ID)')

    @cached_property
    def title(self):
        """Title of CREC document.
        """
        return self._get_by_xpath(
            self._xml_tree, 'string(ns:titleInfo/ns:title)'
        )

    @cached_property
    def title_part(self):
        """Section of daily batch of CREC docs, usually one of "Daily Digest",
        "Extensions of Remarks", "House", "Senate".
        """
        return self._get_by_xpath(
            self._xml_tree, 'string(ns:titleInfo/ns:partName)'
        )

    @cached_property
    def pdf_url(self):
        """Location on gpo.gov for the pdf version of this CREC doc.
        """
        return self._get_by_xpath(
            self._xml_tree,
            'string(ns:location/ns:url[@displayLabel="PDF rendition"])'
        )

    @cached_property
    def html_url(self):
        """Location on gpo.gov for the html version of this CREC doc.
        """
        return self._get_by_xpath(
            self._xml_tree,
            'string(ns:location/ns:url[@displayLabel="HTML rendition"])'
        )

    @cached_property
    def page_start(self):
        """CREC docs are grouped into one large pdf each day, this indicates the
        page on which this document starts (a single page can include more than
        one doc).
        """
        return self._get_by_xpath(
            self._xml_tree,
            'string(ns:part[@type="article"]/ns:extent/ns:start)'
        )

    @cached_property
    def page_end(self):
        """CREC docs are grouped into one large pdf each day, this indicates the
        page on which this document ends (a single page can include more than
        one doc).
        """
        return self._get_by_xpath(
            self._xml_tree,
            'string(ns:part[@type="article"]/ns:extent/ns:end)'
        )

    @cached_property
    def speakers(self):
        """List of names of people identified as speakers in this doc. Names
        usually corrrespond to the ``official_full`` field in bioguide data.
        Can be empty.

        Examples:
            ``['Mitch McConnell', 'Roy Blunt', 'Charles E. Schumer']``
            ``['Charles E. Schumer']``
            ``[]``
        """
        return self._get_by_xpath(
            self._xml_tree, 'ns:name[@type="personal"]/ns:namePart/text()'
        )

    @cached_property
    def speaker_ids(self):
        """Maps a short name version of a speaker's name with their bioguideid,
        this is used for matching segments within this doc to the speaker for
        that segment. Can be empty.

        Examples:
            ``{'Mr. GALLEGO': 'G000574'}``
            ``{'Mr. SMITH': 'S000583', 'Mr. LATTA': 'L000566'}``
            ``{}``
        """
        speaker_ids_ = {}
        persons = self._get_by_xpath(
            self._xml_tree, 'ns:extension/ns:congMember'
        )
        for person in persons:
            parsed_name = self._get_by_xpath(
                person, 'string(ns:name[@type="parsed"])'
            )
            sanitized_name = re.sub(' of .*$', '', parsed_name)
            if person.get('role') == 'SPEAKING':
                speaker_ids_[sanitized_name] = person.get('bioGuideId')
        return speaker_ids_

    @cached_property
    def content(self):
        """The text of this CREC doc (may be plain text or html).
        """
        s3_key = crec_s3_key(self.id.strip('id-') + '.htm', self.date_issued)
        try:
            response = self.s3.get_object(
                Bucket=settings.CREC_STAGING_S3_BUCKET, Key=s3_key
            )
            content = response['Body'].read().decode('utf-8')
            return content
        except ClientError as e:
            # TODO: Proper error handling for missing CREC file.
            print(s3_key)

    @cached_property
    def is_daily_digest(self):
        """True if this doc is a daily digest. The Daily Digest is an
        aggregation of all CREC docs for a day, we omit it in favor of parsing
        each individually.
        """
        tokens = self.id.split('-')
        return any([
            tokens[-1].startswith('PgD'),
            tokens[-2].startswith('PgD'),
            (self.title_part and self.title_part.startswith('Daily Digest'))
        ])

    @cached_property
    def is_front_matter(self):
        """True if this is a front matter page. These are effectively cover
        pages and do not contain relevant data.
        """
        tokens = self.id.split('-')
        if len(tokens) > 0:
            return self.id.split('-')[-1].startswith('FrontMatter')
        else:
            return False

    def is_skippable(self):
        """Returns True if this is one of the type of documents in the daily
        aggregation of CREC docs that does not contain relevant data and should
        not be uploaded to elasticsearch.
        """
        return self.is_daily_digest or self.is_front_matter

    @cached_property
    def textacy_text(self):
        """An instance of ``textacy.Doc`` containing preprocessed data from the
        ``content`` field.
        """
        text = text_utils.preprocess(self.content)
        return textacy.Doc(SPACY_NLP(text))

    @cached_property
    def named_entity_counts(self):
        """A nested-dict mapping named entity type to a histogram dict of any
        named entities of that type contained within ``content``. See
        `https://spacy.io/usage/linguistic-features#section-named-entities`_
        for a list and decriptions of these types.

        Example:

            ::

                {
                    'PERSON': {
                        'Benjamin S. Carson': 1, 'Elaine L. Chao': 1
                    },
                    'ORG': {
                        'Senate': 15, 'Chamber Action Routine Proceedings': 1
                    }
                }
        """
        named_entities = text_utils.get_named_entities(self.textacy_text)
        named_entity_counts_ = {}
        if any(named_entities):
            named_entity_types = text_utils.get_named_entity_types(
                named_entities
            )
            named_entity_freqs = text_utils.get_named_entity_frequencies(
                named_entities
            )
            for ne_type in named_entity_types.keys():
                # TODO: Better type name for type == ''?
                if ne_type == 'PERSON':
                    named_entity_counts_[ne_type] = {
                        text_utils.camel_case(ne, force=False): named_entity_freqs[ne]
                        for ne in named_entity_types[ne_type]
                    }
                else:
                    named_entity_counts_[ne_type] = {
                        ne: named_entity_freqs[ne]
                        for ne in named_entity_types[ne_type]
                    }
        return named_entity_counts_

    @cached_property
    def noun_chunks_counts(self):
        """A dict mapping noun chunks type to number of occurrences within
        ``content``.

        Example:

            ::

                {
                    'united states trade representative': 1,
                    'unanimous consent agreement': 1,
                }
        """
        noun_chunks = text_utils.get_noun_chunks(self.textacy_text)
        noun_chunks = text_utils.named_entity_dedupe(
            noun_chunks,
            chain(*[d.keys() for d in self.named_entity_counts.values()])
        )
        return dict(Counter(noun_chunks))

    @cached_property
    def segments(self):
        """List of segments of ``content`` attributed to individual speakers.

        Speakers can be indviduals identified by name (and usually bioGuideId)
        or generic speakers (roles). A sentence containing an individual or
        generic speaker (exact or approximate match) marks the beginning of
        new segment.

        Example:

            ::
                [
                    {
                        'id': 'id-CREC-2017-01-20-pt1-PgS348-1',
                        'speaker': 'Mr. McCONNELL',
                        'text': 'THANKING FORMER PRESIDENT OBAMA. Mr. McCONNELL.Mr.  President, I wish to offer a few words regarding...',
                        'bioguide_id': 'M000355'
                    },
                    {
                        'id': 'id-CREC-2017-01-20-pt1-PgS348-2-1',
                        'speaker': 'Mr. DURBIN',
                        'text': 'NOMINATIONS. Mr. DURBIN.  Mr. President, I listened carefully to the statement by theRepublican lead...',
                        'bioguide_id': 'D000563'
                    }
                ]
        """
        sents = (sent.string for sent in self.textacy_text.spacy_doc.sents)
        previous = None
        current = None
        segment_index = 0
        segment_sents = []
        segments_ = []
        individual_speakers = self.speaker_ids.keys()
        for sent in chain(sents, ('<EOF>',)):
            speaker = next(
                filter(lambda person: person in sent, chain(
                    individual_speakers, GENERIC_SPEAKERS)), None)
            if speaker is not None:
                current = speaker
                logger.debug(
                    'Found speaker: {}, previous speaker {}'.format(current, previous))
            else:
                speaker, score = process.extractOne(sent, chain(
                    individual_speakers, GENERIC_SPEAKERS))
                if score > APPROX_MATCH_THRESHOLD:
                    current = speaker
                    logger.debug(
                        'Found speaker: {} (approx. score {}/100), previous speaker: {}'.format(
                            current, score, previous))
            if previous != current or sent == '<EOF>':
                if segment_sents:
                    segment_index += 1
                    segment = {
                        'id': '{}-{}'.format(self.id, segment_index),
                        'speaker': previous,
                        'text': ' '.join(segment_sents),
                        'bioguide_id': None,
                    }
                    if segment['speaker'] in self.speaker_ids:
                        segment['bioguide_id'] = self.speaker_ids[segment['speaker']]
                    segments_.append(segment)
                previous = current
                segment_sents = [sent]
            else:
                segment_sents.append(sent)
        return segments_

    def to_es_doc(self):
        """Returns the CRECParser as a dict ready to be uploaded to
        elasticsearch.

        Returns:
            dict: A dict representation of this document.
        """
        return CRECDoc(
            title=self.title,
            title_part=self.title_part,
            date_issued=self.date_issued,
            content=self.content,
            crec_id=self.id,
            pdf_url=self.pdf_url,
            html_url=self.html_url,
            page_start=self.page_start,
            page_end=self.page_end,
            speakers=','.join(self.speakers),
            segments=self.segments,
        )


def upload_speaker_word_counts(crec_parser):
    """Creates new entries of the SpeakerWordCounts ORM model containing
    counts of named entities and noun chunks within this document.

    Args:
        crec_parser (:class:`parser.crec_parser.CRECParser`): A CRECParser
            instance representing a single CREC document.
    """
    if crec_parser.speaker_ids:
        named_entities = {'named_entities_{0}'.format(ne_type): counts
                          for ne_type, counts in crec_parser.named_entity_counts.items()}
        for bioguide_id in crec_parser.speaker_ids.values():
            speaker_counts = SpeakerWordCounts(
                bioguide_id=bioguide_id,
                crec_id=crec_parser.id,
                date=crec_parser.date_issued,
                named_entities=json.dumps(crec_parser.named_entity_counts),
                noun_chunks=json.dumps(crec_parser.noun_chunks_counts)
            )
            speaker_counts.save()


def extract_crecs_from_mods(mods_file_obj, xml_namespace=DEFAULT_XML_NS):
    """Takes a file-like object containing mods.xml data for a single day,
    extracts each "constituent" (a single CREC document from that day) and
    creates a new CRECParser instance for that document. Returns all CRECParser
    instances created for a single day as a list.

    Args:
        mods_file_obj (file): An open file, StringIO or BytesIO buffer
            containing mods.xml data.
        xml_namespace (dict): The xml_namespaces argument to use with the lxml
            parser.

    Returns:
        list of :class:`parser.crec_parser.CRECParser`: A list of parsed CREC
            docs for a single day.
    """
    xml_tree = None
    xml_tree = etree.parse(mods_file_obj)
    constituents = xml_tree.xpath(
        '//ns:relatedItem[@type="constituent"]',
        namespaces=xml_namespace,
    )
    date_issued_str = xml_tree.xpath(
        'string(//ns:originInfo/ns:dateIssued)',
        namespaces=xml_namespace,
    )
    date_issued = datetime.strptime(date_issued_str, '%Y-%m-%d')
    return [CRECParser(c, date_issued) for c in constituents]
