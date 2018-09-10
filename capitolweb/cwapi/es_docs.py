from django.conf import settings
from elasticsearch_dsl import Search, Index, DocType, Date, Text, Nested
from elasticsearch_dsl import InnerObjectWrapper
from elasticsearch_dsl.connections import connections

connections.create_connection(
    hosts=[settings.ES_URL],
    **settings.ES_CONNECTION_PARAMS
)

def make_search():
    """Convenience function for returning a base :cls:`elasticsearch_dsl.Search`
    instance using the index name in django settings.

    Returns:
        :cls:`elasticsearch_dsl.Search`: An elasticsearch_dsl Search instance.
    """
    return Search(index=settings.ES_CW_INDEX)


def get_term_count_agg(results):
    """Convenience function for extracting the date histogram from the a term
    count aggregation.

    Returns:
        list: A list of aggregation buckets containing both the date and the
            aggregated term count for that bucket.
    """
    return results.get('aggregations', {}).get('term_counts_by_day', {}).get('buckets')


def term_counts_script(term):
    """Returns the complete configuration for an elasticsearch scripted metric
    aggregation script (https://www.elastic.co/guide/en/elasticsearch/reference/5.1/search-aggregations-metrics-scripted-metric-aggregation.html).
    that will count the occurences of the provided term in every CREC document
    in the bucket. The script parts are written in painless. Note: because
    painless limits total iterations in a loop, this will not return accurate
    counts for docs that contain more than 4999 tokens (the overwhelming
    majority of CREC documents fall below this limit).

    Args:
        term (str): A search term to look for in the "content" field of each
            CREC document.

    Returns:
        dict: The content for a scripted metric aggregation part of an
            elasticsearch query.
    """
    return {
        'params': {
            '_agg': {},
            'term': term
        },
        'init_script': '''
            params._agg.counts = [];
        ''',
        'map_script': '''
            def tokens = new StringTokenizer(params._source.content.toLowerCase());
            int i = 0;
            int n = 0;
            while (tokens.hasMoreTokens() && n < 4999) {
                if (tokens.nextToken().toLowerCase() == params.term) {
                    i += 1
                }
                n += 1;
            }
            params._agg.counts.add(i)
        ''',
        'combine_script': '''
            int j = 0;
            for (i in params._agg.counts) {
                j += i
            }
            return j
        ''',
        'reduce_script': '''
            int j = 0;
            for (i in params._aggs) {
                j += i ?: 0
            }
            return j;
        ''',
    }


class CRECDoc(DocType):
    """An elasticsearch_dsl document model for CREC documents.
    """

    title = Text()
    title_part = Text()
    date_issued = Date()
    content = Text(fielddata=True)
    crec_id = Text()
    pdf_url = Text()
    html_url = Text()
    page_start = Text()
    page_end = Text()
    speakers = Text()
    segments = Nested(
        properties={
            'segment_id': Text(),
            'speaker': Text(),
            'text': Text(),
            'bioguide_id': Text()
        }
    )

    class Meta:
        index = settings.ES_CW_INDEX


def get_term_count_in_doc(es_conn, term, start_date, end_date):
    """Queries elasticsearch with a scripted metric aggregation, bucketed by
    day, that counts the total number of occurrences of the provided term in
    every CREC document in that bucket.

    Args:
        es_conn :cls:`elasticsearch.Elasticsearch`: A connection to an
            elasticsearch cluster.
        term (str): Search term.
        start_date (date): Start of date range.
        end_date (date): End of date range.

    Returns:
        dict: The response from the elasticsearch query.
    """
    term = term.lower()
    results = es_conn.search(
        index=CRECDoc._doc_type.index,
        doc_type=CRECDoc._doc_type.name,
        body={
            'size': 0,
            'query': {
                'bool': {
                    'must': {'term': {'content': term}},
                    'filter': {
                        'range': {
                            'date_issued': {
                                'gte': start_date.strftime('%Y-%m-%dT00:00:00Z'),
                                'lte': end_date.strftime('%Y-%m-%dT00:00:00Z')
                            }
                        }
                    }
                }
            },
            'aggregations': {
                'term_counts_by_day': {
                    'date_histogram': {
                        'field': 'date_issued',
                        'interval': 'day'
                    },
                    'aggregations': {
                        'term_counts': {
                            'scripted_metric': term_counts_script(term)
                        }
                    }
                }
            }
        }
    )
    return results
