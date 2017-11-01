from __future__ import print_function

import logging
from datetime import datetime
from collections import Counter

import boto3
import spacy
import textacy
from lxml import etree

import capitolweb.workers.text_utils as text_utils


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


CREC_PREFIX_TEMPLATE = 'crec/%Y/%m/%d/crec'
CREC_KEY_TEMPLATE = '{prefix}/{id}.htm'


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
        logging.info('Parsing mods file...')
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
            record['s3_key'] = s3_key
            failed_retrievals = []
            try:
                response = self.s3.get_object(Bucket=self.bucket, Key=s3_key)
                record['content'] = response['Body'].read().decode('utf-8')
            except Exception as e:
                failed_retrievals.append(s3_key)

        if len(failed_retrievals) > 0:
            logging.error(
                'Failed to retieve {0}/{1} crec docs.'.format(
                    len(failed_retrievals), len(records)
                )
            )
            for s3_key in failed_retrievals:
                logging.error('Failed retrieval: "{0}".'.format(s3_key))
        else:
            logging.info('All crec retrievals succeeded.')

        for record in records:
            if (record['ID'].split('-')[-1].startswith('PgD') or
                record['ID'].split('-')[-2].startswith('PgD')):
                # dont process daily digests
                logging.info('Not processing Daily Digest %s', record['ID'])
                continue

            elif record['ID'].split('-')[-1].startswith('FrontMatter'):
                # dont process front matters or pages with no content
                logging.info('Not processing Front Matter %s', record['ID'])
                continue

            elif (record.get('content') is None or 'content' not in record.keys()):
                # dont process fpages with no content
                logging.info('Not processing %s. No content found.', record['ID'])
                continue

            text = text_utils.preprocess(record['content'])
            textacy_text = textacy.Doc(self.nlp(text))

            # Extract named entities and their types & frequencies
            named_entities = text_utils.get_named_entities(textacy_text)
            if any(named_entities):
                named_entity_types = text_utils.get_named_entity_types(named_entities)
                named_entity_freqs = text_utils.get_named_entity_frequencies(named_entities)

                for type_ in named_entity_types.keys():
                    ne_type = 'named_entities_' + type_
                    nes = []
                    if type_ == 'PERSON':
                        nes = [(ne.title(), named_entity_freqs[ne])
                               for ne in named_entity_types[type_]]
                    else:
                        nes = [(ne, named_entity_freqs[ne])
                               for ne in named_entity_types[type_]]
                    nes.sort(key=lambda x: x[1], reverse=True)
                    record[ne_type] = str(nes)

            # Extract noun phrases & their frequencies
            noun_chunks = text_utils.get_noun_chunks(textacy_text)
            noun_chunks = text_utils.named_entity_dedupe(noun_chunks, named_entity_freqs.keys())
            record['noun_chunks'] = str(Counter(noun_chunks).most_common())

        return records
