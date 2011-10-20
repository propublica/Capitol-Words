import re

class JSONPMiddleware(object):
    '''
    Middleware to handle jsonp requests on projects while still providing for
    caching of content.  What happens here is:

    1. Some page makes a jquery $.getJSON request to foo.json?callback=? on projects
    2. jquery replaces callback=? with callback=foo, where foo is random
    3. Projects middleware detects that a .json request occurred with a callback,
       strips out and saves the callback name from the GET variables
    4. URL, view, and caching logic proceed as normal without the callback variable,
       returning an HttpResponse with pure json content
    5. Projects middleware wraps foo(...) around the json per the callback variable
       and returns to the user
    '''
    def process_request(self, request):
        if not request.path.endswith('.json') or 'callback' not in request.GET:
            return None

        # Store on request object
        request.jsonp_callback = request.GET['callback']

        # Remove from GET vars
        mutable = request.GET._mutable
        request.GET._mutable = True
        del request.GET['callback']
        try: # jquery puts this in too
            del request.GET['_']
        except KeyError:
            pass
        request.GET._mutable = mutable

        return None

    def process_response(self, request, response):
        try:
            callback = request.jsonp_callback

        except AttributeError:
            return response

        else:
            response.content = '%s(%s)' % (re.sub(r'[^\w_]', '', callback), response.content.decode('utf-8'))
            return response
