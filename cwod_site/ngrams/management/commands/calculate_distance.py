from itertools import combinations
from math import sqrt
from optparse import make_option
from scipy.spatial.distance import cosine as cosine_distance

from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction
from django.template.defaultfilters import title
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
        a = self.get_vector(self.keypair[0])
        b = self.get_vector(self.keypair[1])
        # we store these as 1=congruent
        return 1 - cosine_distance(a, b)


    # def cosine_distance(self, a, b):
    #     '''Calculates the distance between n-dimensional vectors a, b
    #        http://stackoverflow.com/questions/1823293/optimized-method-for-calculating-cosine-distance-in-python
    #        '''
    #     if len(a) != len(b):
    #         raise ValueError, "a and b must be the same length"
    #     numerator = 0
    #     denoma = 0
    #     denomb = 0
    #     for i in range(len(a)):
    #         ai = a[i]
    #         bi = b[i]
    #         numerator += ai*bi
    #         denoma += ai*ai
    #         denomb += bi*bi
    #     result = 1 - numerator / (sqrt(denoma)*sqrt(denomb))
    #     return result

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
    )

    def handle(self, *args, **options):
        field = options.get('field')
        if not field:
            raise ValueError('You must specify a field! Options are: date, month, state, bioguide')
        values_to_compare = [value.strip() for value in options.get('values').split(',') if value]

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
        if values_to_compare:
            params = {'%s__in' % get_field(field): values_to_compare}
            ngrams = get_model(field).objects.filter(**params)
        else:
            ngrams = get_model(field).objects.all()

        return ngrams

