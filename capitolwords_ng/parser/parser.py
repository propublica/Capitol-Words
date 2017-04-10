"""Parses a mods.xml file from the daily CREC dumps.

"""

from __future__ import print_function

import json
import logging
import argparse
import urlparse
from functools import partial

import elasticsearch
from lxml import etree


DEFAULT_XML_NS = {'ns': 'http://www.loc.gov/mods/v3'}


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


class OutputDestinationError(Exception):
    pass

def stdout_outputter(records):
    """Outputs records to stdout in json format."""

    for r in records:
        print(json.dumps(r))

def es_outputter(es_conn, index, records):
    """Writes records into ES_CONN.

    Note this isn't exactly an outputter since it takes an
    Elasticsearch connection argument.

    """

    for r in records:
        es_conn.index(index=index, doc_type='crec', id=r['ID'], body=r)

def make_outputter(spec):
    """Returns an outputter function given an output SPEC.

    Outputter functions have one argument, the record they're supposed to output.

    If SPEC is '-' then returns a stdout outputter.

    If SPEC is 'es://HOST:PORT/INDEX' returns an Elasticsearch outputter.

    Otherwise, raises OutputDestinationError.

    """

    if spec == '-':
        logging.debug("using stdout outputter")

        return stdout_outputter
    elif spec.startswith('es://'):
        logging.debug("using Elasticsearch outputter")

        comps = urlparse.urlparse(spec)
        if comps.scheme != 'es':
            # if we get here I have no clue what's going on, because
            # the string started with 'es://'
            raise OutputDestinationError(
                "impossible error parsing Elasticsearch output spec %s",
                spec,
            )
        es_host = comps.netloc
        index = comps.path.strip('/')

        if not es_host or not index:
            raise OutputDestinationError("couldn't extract host and index from %s", spec)

        logging.debug("connecting to Elasticsearch host %s index %s", es_host, index)
        es_conn = elasticsearch.Elasticsearch([es_host])
        es_conn.info()
        return partial(es_outputter, es_conn, index)
    else:
        raise OutputDestinationError("unknown output destination %s" % spec)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Extract constituent records from mods.xml.",
    )
    parser.add_argument('--loglevel', type=str, default='info',
                        help="log level")
    parser.add_argument('--mods', type=str, required=True,
                        help="xml file to load")
    parser.add_argument('--out', type=str, default='-',
                        help="output destination (defaults to stdout, use es://HOST:PORT for Elasticsearch)")
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel.upper())

    outputter = make_outputter(args.out)

    tree = etree.parse(open(args.mods, 'r'))
    constituents = tree.xpath(
        '//ns:relatedItem[@type="constituent"]',
        namespaces=DEFAULT_XML_NS,
    )
    date_issued = tree.xpath(
        'string(//ns:originInfo/ns:dateIssued)',
        namespaces=DEFAULT_XML_NS,
    )

    logging.info("date issued: %s", date_issued)

    records = [
        xpath_parse(
            r,
            {
                'ID': 'string(@ID)',
                'title': 'string(ns:titleInfo/ns:title)',
                'title_part': 'string(ns:titleInfo/ns:partName)',
                'pdf_url': 'string(ns:location/ns:url[@displayLabel="PDF rendition"])',
                'html_url': 'string(ns:location/ns:url[@displayLabel="HTML rendition"])',
                'page_start': 'string(ns:part[@type="article"]/ns:extent/ns:start)',
                'page_end': 'string(ns:part[@type="article"]/ns:extent/ns:end)',
                'speakers': 'ns:name[@type="personal"]/ns:namePart/text()',
            },
            namespaces={'ns': 'http://www.loc.gov/mods/v3'},
        )
        for r in constituents
    ]
    for r in records:
        r['date'] = date_issued

    outputter(records)
