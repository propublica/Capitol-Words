"""
    Python library for interacting with version 3 of the Capitol Words API

    Based heavily on the Sunlight Labs python-datacatalog wrapper:
    http://github.com/sunlightlabs/python-datacatalog/
"""

__author__ = "Joshua Ruihley <jruihley@sunlightfoundation.com>"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2010 Sunlight Foundation"
__license__ = "BSD"

import urllib, httplib2
try:
    import json
except ImportError:
    import simplejson as json
    
class ApiError(Exception):
    """ Exception for API errors """

class capitolwords(object):

    def __init__(self, api_key=None, domain='capitolwords.org/api'):
        self.api_key = api_key
        self.domain = domain
        self.last_call = {}

    def store_last_call(self, url, params, response):
        self.last_call['url'] = url
        self.last_call['params'] = params
        self.last_call['response'] = response

    def _apicall(self, func, params=None, method='GET'):
        param_str = ''
        if params:
            params = dict([(k,v) for (k,v) in params.iteritems() if v is not None])
            param_str = '?%s' % urllib.urlencode(params)
        url = 'http://%s/%s.json%s' % (self.domain, func, param_str)
        print url

        try:
            h = httplib2.Http()
            response, content = h.request(url, method=method, headers=None, body=None)
            obj = json.loads(content)
            self.store_last_call(url, params, response)

            if 'errors' in obj:
                raise ApiError(obj['errors'], url, method, param_str)
            else:
                return obj
        except httplib2.HttpLib2Error, e:
            raise ApiError(e.read())
        except ValueError, e:
            print e
            raise ApiError('Invalid Response')
            
    def phrase_by_date_range(self, **params):
        result = capitolwords._apicall(self, 'dates', params)['results']
        return result

    def timeline(self, **params):
        result = capitolwords._apicall(self, 'chart/timeline', params)['results']
        return result

    def piechart(self, **params):
        result = capitolwords._apicall(self, 'chart/pie', params)['results']
        return result
        
    def phrase_by_entity_type(self, entity_type, **params):
        result = capitolwords._apicall(self, 'phrases/%s' % entity_type, params)['results']
        return result
        
    def top_phrases(self, **params):
        result = capitolwords._apicall(self, 'phrases', params)
        return result
        
    def get_legislator(self, **params):
        result = capitolwords._apicall(self, 'legislators', params)
        return result

    def wordtree(self, **params):
        result = capitolwords._apicall(self, 'tree', params)['results']
        return result

    def text(self, **params):
        result = capitolwords._apicall(self, 'text', params)['results']
        return result

    def _similar(self, **params):
        result = capitolwords._apicall(self, '_similar', params)['results']
        return result
