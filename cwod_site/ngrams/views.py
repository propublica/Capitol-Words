import re

from piston.handler import BaseHandler
from piston.resource import Resource

from ngrams import models



class NgramApiException(Exception):
    pass


class GenericHandler(Resource):

    # These are the entities by which queries can be filtered.
    ENTITIES = {'state': 'speaker_state',
                'party': 'speaker_party',
                'bioguide_id': 'speaker_bioguide',
                'congress': 'congress',
                'year': 'year',
                'month': 'yearmonth',
                'date': 'date', }

    # (size of a tokenized phrase) + 1 will correspond to
    # the index of the name of the ngram field.
    NGRAM_FIELDS = ['unigrams',
                    'bigrams',
                    'trigrams',
                    'quadgrams',
                    'pentagrams', ]


    def get_modelname(self, n, entities):
        """Using the number of tokens in the ngram (n)
        and a list of the entities by which we'll be filtering,
        construct the name of the model to query.
        """
        # Granularity is only used in PhraseOverTime queries,
        # but we need to know about it here to get the model name.
        if getattr(self, 'granularity', None) is not None:
            entities.append(granularity)

        # The list of entities in model names are always
        # in alphabetical order.
        entities.sort(key=lambda x: x[0])

        ngram_field = self.NGRAM_FIELDS[n-1]

        # Example model names: UnigramsByCountChamberDate,
        # TrigramsByCountBioguideCongress, PentagramsByCountYear
        return '%sByCount%s' % (ngram_field.title(),
                                ''.join([x.title() for x in entities])
                               )


    def get_model(self, tokens, entities):
        """Get the model object from ngrams.models
        using the model name.

        If it doesn't exist, it's likely that there
        is a bad combination of entities.
        """
        self.modelname = self.get_modelname(len(tokens), entities)
        try:
            return getattr(models, self.modelname)
        except AttributeError:
            raise NgramApiException()


    def clean_tokens(self, tokens):
        """Remove punctuation-only tokens.
        """
        return [re.sub(r',', '', x.lower().rstrip('-').strip("'"))
                for x in tokens
                if re.search(r'[a-z0-9.?!]', x.lower())]


    def tokenize_phrase(self, phrase):
        """Adapted From Natural Language Processing with Python
        This is the same as the regex used to tokenize text
        in the script that creates Solr documents, but without
        capturing groups.
        """
        regex = r'''(?x)
        (?:H|S)\.\ ?(?:(?:J|R)\.\ )?(?:Con\.\ )?(?:Res\.\ )?\d+ # Bills
      | (?:[A-Z]\.)+                                            # Abbreviations (U.S.A., etc.)
      | [A-Z]+\&[A-Z]+                                          # Internal ampersands (AT&T, etc.)
      | (?:Mr\.|Dr\.|Mrs\.|Ms\.)                                # Mr., Mrs., etc.
      | \d*\.\d+                                                # Numbers with decimal points.
      | \d\d?:\d\d                                              # Times.
      | \$?[,\.0-9]+                                            # Numbers with thousands separators, (incl currency).
      | (?:(?:(?:a|A)|(?:p|P))\.(?:m|M)\.)                      # a.m., p.m., A.M., P.M.
      | \w+(?:(?:-|')\w+)*                                      # Words with optional internal hyphens.
      | \$?\d+(?:\.\d+)?%?                                      # Currency and percentages.
      | \.\.\.                                                  # Ellipsis
      | [][.,;"'?(?:):-_`]
        '''
        regexp = re.compile(regex, re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE)
        return self.clean_tokens(regexp.findall(phrase.lower()))


    def do_query(self, params, fields, ngram=None):
        self.tokens = self.tokenize_phrase(phrase)
        self.model = self.get_model(self.tokens, [x[0] for x in params])
        self.ngram = ' '.join(self.tokens)
        if ngram:
            params.append(('ngram', ngram))
        fields.append('count')
        return self.model.objects.filter(**dict(params)) \
                                 .values(*fields)

    def get_params(self, request):
        params = []
        for k, v in self.ENTITIES.iteritems():
            if k in request.GET:
                if request.GET[k]: # Make sure value isn't blank
                    params.append((k, request.GET[k]))
        return params


class PhraseOverTimeHandler(GenericHandler):

    def read(self, request, *args, **kwargs):
        phrase = request.GET.get('phrase')
        params = self.get_params()
        self.granularity = request.GET.get('granularity', 'date')
        return self.do_query(params, [self.granularity, ], phrase)


class PhraseByCategoryHandler(GenericHandler):

    def read(self, request, *args, **kwargs):
        phrase = request.GET.get('phrase')
        field = request.GET.get('entity_type')
        params = self.get_params()
        return self.do_query(params, [field, ], phrase)


class PopularPhraseHandler(GenericHandler):

    def read(self, request< *args, **kwargs):
        params = self.get_params()
        return self.do_query(params, ['ngram', ])
