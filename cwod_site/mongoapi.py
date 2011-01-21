from operator import itemgetter
from collections import defaultdict

import pymongo
from pymongo import Connection
from pymongo.code import Code



field = lambda n: ['unigrams', 'bigrams', 'trigrams', 'quadgrams', 'pentagrams'][n-1]

entities = {'state': 'speaker_state',
            'party': 'speaker_party',
            'legislator': 'speaker',
            'bioguide': 'speaker_bioguide', 
            'cr_pages': 'pages',
            'volume': 'volume',
            }

connection = Connection()
db = connection['test-cwod-new']


def phrase_counts(*args, **kwargs):
    n = kwargs.get('n', 1)
    limit = kwargs.get('limit', 50)
    offset = kwargs.get('offset', 0)

    params = {'n': n, }

    for k, v in entities.iteritems():
        if k in kwargs:
            params[v] = kwargs[k]

    collection = db[field(n)]
    print collection

    results = collection.group(['n', ],
                     params,
                     {'ngrams': {}},
                     """function (obj, prev) {
                            if (prev.ngrams.hasOwnProperty(obj.ngram)) {
                                prev.ngrams[obj.ngram] += obj.count;
                            } else {
                                prev.ngrams[obj.ngram] = obj.count;
                            }
                     }""")

    ngrams = results[0]['ngrams']
    return sorted(ngrams.items(), key=itemgetter(1), reverse=True)[offset:limit]



def phrase_by_category(*args, **kwargs):
    ngram = kwargs.get('phrase')

    entity = kwargs.get('entity')
    fieldname = entities[entity]

    params = {'ngram': ngram, }

    for k, v in entities.iteritems():
        if k in kwargs:
            params[v] = kwargs[k]

    n = len(ngram.split())

    collection = db[field(n)]

    results = collection.group([fieldname, ],
                               params,
                               {'entities': {}},
                               """function (obj, prev) {
                                   if (prev.entities.hasOwnProperty(obj.%(fieldname)s)) {
                                       prev.entities[obj.%(fieldname)s] += obj.count;
                                   } else {
                                       prev.entities[obj.%(fieldname)s] = obj.count;
                                   }
                               }""" % locals())
    return [result['entities'] for result in results]



def phrase_over_time(*args, **kwargs):
    ngram = kwargs.get('phrase')

    params = {'ngram': ngram, }

    for k, v in entities.iteritems():
        if k in kwargs:
            params[v] = kwargs[k]

    n = len(ngram.split())

    collection = db[field(n)]

    periods = {'day': "obj.date.getFullYear()+'-'+(obj.date.getMonth()+1)+'-'+obj.date.getDate()",
               'month': "obj.date.getFullYear() + '-' + (obj.date.getMonth()+1)",
               'year': 'obj.date.getFullYear()',
               }
    func = periods[kwargs.get('granularity', 'day')]

    results = collection.group(['period', ],
                                params,
                                {'periods': {}},
                                """function (obj, prev) {
                                    if (prev.periods.hasOwnProperty(%(func)s)) {
                                        prev.periods[%(func)s] += obj.count;
                                    } else {
                                        prev.periods[%(func)s] = obj.count;
                                    }
                                }""" % locals())
    print results


def _main():
    ngrams = phrase_counts(n=1, limit=2500)
    for ngram, count in ngrams:
        print ngram, count
    #results = phrase_by_category(phrase='health care', entity='bioguide', party='Republican')
    #for result in results:
    #    print result
    #phrase_over_time(phrase='united states', granularity='day')


if __name__ == '__main__':
    _main()
