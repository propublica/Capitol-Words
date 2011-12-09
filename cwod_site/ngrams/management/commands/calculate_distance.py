from itertools import combinations, chain
from math import sqrt, isnan
from optparse import make_option
from scipy.spatial.distance import cosine as cosine_distance

from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction

from ngrams.models import *

class Calculator(object):
    def __init__(self, field, models, keypair):
        self.field = field
        self.models = models
        self.keypair = keypair
        self.ngram_map = {}
        for model in models:
            key = str(model.__dict__[get_field(self.field)])
            try:
                self.ngram_map[model.ngram][key] = model.tfidf
            except KeyError:
                self.ngram_map[model.ngram] = {key: model.tfidf}

    def calculate(self):
        v1 = self.get_vector(self.keypair[0])
        v2 = self.get_vector(self.keypair[1])
        # we store these as 1=congruent
        distance = 1 - cosine_distance(v1, v2)
        if isnan(distance):
            distance = 0
        return distance

    def get_vector(self, key):
        return tuple([ngram.get(key, 0) for ngram in self.ngram_map.values()])

def get_model(field):
    return {
        'date': NgramsByDate,
        'month': NgramsByMonth,
        'state': NgramsByState,
        'bioguide': NgramsByBioguide,
        }[field]

def get_distance_model(field):
    return {
        'date': DistanceDate,
        'month': DistanceMonth,
        'state': DistanceState,
        'bioguide': DistanceBioguide,
        }[field]


def get_field(field):
    try:
        return {
            'bioguide': 'bioguide_id'
            }[field]
    except KeyError:
        return field

def list_active_legislators_first():
    query = 'select bioguide_id from bioguide_legislatorrole group by bioguide_id order by max(end_date) desc, bioguide_id'
    from MySQLdb import Connection
    cursor = Connection('localhost', 'capwords', 'capwords', 'capwords').cursor()
    cursor.execute(query)
    results = [x[0] for x in cursor.fetchall()]
    return results

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--field',
                action='store',
                dest='field',
                default=None,
                help='Facet to calculate distance on'),
            make_option('--values',
                action='store',
                dest='values',
                default='',
                help='Specific values to limit calculations among'),
            make_option('--test',
                action='store',
                dest='test',
                default=False,
                help='Set this to true to skip writing to the database'),
    )

    def handle(self, *args, **options):
        field = options.get('field')
        if not field:
            raise ValueError('You must specify a field! Options are: date, month, state, bioguide')
        values_to_compare = [value.strip() for value in options.get('values').split(',') if value]
        test = options.get('test')

        if test:
            print '*** This is a test; the database will not be updated ***'

        if field == 'bioguide':
            cursor = connections['default'].cursor()
            query = 'SELECT bioguide_id FROM bioguide_legislatorrole GROUP BY bioguide_id ORDER BY max(end_date) DESC, bioguide_id'
        else:
            cursor = connections['ngrams'].cursor()
            query = 'SELECT DISTINCT %s FROM ngrams_ngramsby%s' % (get_field(field), field)

        if values_to_compare: #combinations of new values against all current values
            keys1 = set(values_to_compare)
            cursor.execute(query)
            keys2 = set([str(key[0]) for key in cursor.fetchall() if key[0]])
            keys = []
            for a in keys1:
                for b in keys2:
                    if a != b:
                        keys.append((a, b))
            pairs = tuple(keys)
        else: #combinations of all values against all other values
            cursor.execute(query)
            keys = set([str(key[0]) for key in cursor.fetchall() if key[0]])
            pairs = combinations(keys, 2)

        for keypair in pairs:
            with transaction.commit_on_success():
                current_models = self._get_models(field, keypair)
                calculator = Calculator(field, current_models, keypair)
                distance = calculator.calculate()
                if not test:
                    obj1, created1 = get_distance_model(field).objects.get_or_create(a=keypair[0],
                                                                                     b=keypair[1],
                                                                                     defaults={
                                                                                         'cosine_distance': distance,
                                                                                         })
                    if not created1:
                        obj1.__dict__.update({'cosine_distance': distance})
                        obj1.save()
                    obj2, created2 = get_distance_model(field).objects.get_or_create(a=keypair[1],
                                                                                     b=keypair[0],
                                                                                     defaults={
                                                                                         'cosine_distance': distance,
                                                                                         })
                    if not created2:
                        obj2.__dict__.update({'cosine_distance': distance})
                        obj2.save()

                print "%s to %s: %s" % (keypair[0], keypair[1], distance)

    def _get_models(self, field, values_to_compare):
        '''in most cases, gets the top 1-grams for each side of the comparison.
           Otherwise gets all 1-grams. Limiting is meant to reduce noise.
           '''
        if values_to_compare and len(values_to_compare) is not 2:
            raise ValueError('_get_models takes 2 values!')
        if values_to_compare:
            params1 = {get_field(field): values_to_compare[0], 'n': 1}
            ngrams1 = get_model(field).objects.filter(**params1).order_by('-tfidf')
            params2 = {get_field(field): values_to_compare[1], 'n': 1}
            ngrams2 = get_model(field).objects.filter(**params2).order_by('-tfidf')
            ngrams = list(chain(ngrams1, ngrams2))
        else:
            ngrams = get_model(field).objects.filter(n=1).order_by('-count')

        return ngrams

