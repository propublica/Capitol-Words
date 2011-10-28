import re

from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.defaultfilters import slugify

def get_entry_detail_url(origin_url, title):
    crec = origin_url.split('/')[-1].replace('.htm', '')
    m = re.search(r'CREC-(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d)-pt\d-Pg(?P<page_id>.*?)$', crec)
    if not m:
        return ''
    kwargs = m.groupdict()
    kwargs['slug'] = slugify(title)[:50]
    try:
        url = reverse('cwod_entry_detail', kwargs=kwargs)
    except NoReverseMatch:
        url = ''
    return url

def flatten_param_dicts(qdict, allowed_keys):
    '''hacks rails-like foo[property] functionality into GET & POST params'''
    for k, v in qdict.items():
        if '[' in k:
            match = re.match(r'(?P<key1>\w+?)\[(?P<key2>\w+?)\](?P<is_arr>\[\])?', k)
            if match and match.group('key1') in allowed_keys:
                key1 = str(match.group('key1'))
                key2 = str(match.group('key2'))
                is_arr = str(match.group('is_arr'))
                try:
                    qdict[key1]
                except KeyError:
                    qdict[key1] = {}
                if is_arr != 'None':
                    qdict[key1][key2] = qdict.getlist(k)
                else:
                    qdict[key1][key2] = str(v)
                del qdict[k]
    return qdict