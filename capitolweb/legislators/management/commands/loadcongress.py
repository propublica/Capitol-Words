from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from legislators.models import State, CongressPerson, ExternalId, Term
from legislators.importer import load_legislators_current, load_legislators_past

date_format = '%Y-%m-%d'


def make_person(bio, name):

    person = CongressPerson(first_name=name['first'], last_name=name['last'])

    if 'official_full' in name:
        person.official_full = name['official_full']
    if 'middle' in name:
        person.middle_name = name['middle']
    if 'suffix' in name:
        person.suffix = name['suffix']
    if 'nickname' in name:
        person.nickname = name['nickname']

    person.gender = bio['gender']
    if 'religion' in bio:
        person.religion = bio['religion']
    if 'birthday' in bio:
        person.birthday = bio['birthday']

    person.save()
    return person


def make_term(person, term):
    defaults = {}
    state = State.objects.get(short=term['state'])
    start = datetime.strptime(term['start'], date_format)
    end = datetime.strptime(term['end'], date_format)
    for p in ['party', 'state_rank', 'district', 'caucus', 'address', 'office', 'phone', 'fax',
              'contact_form', 'rss_url', 'url']:
        if p in term:
            defaults[p] = term[p]
    if 'class' in term:
        defaults['election_class'] = term['class']

    obj, created = person.terms.update_or_create(
        state=state, start_date=start, end_date=end, type=term['type'], defaults=defaults)


def load_data(data, out):
    for rep in data:
        defaults = {}
        defaults.update(rep['name'])
        defaults.update(rep['bio'])
        print(rep['name'])
        obj, created = CongressPerson.objects.update_or_create(
            bioguide_id=rep['id']['bioguide'],
            defaults=defaults,
        )
        for k, v in rep['id'].items():
            obj.external_ids.update_or_create(type=k, value=v)
        for term in rep['terms']:
            make_term(obj, term)


class Command(BaseCommand):
    help = 'Loads congress yaml files'

    def handle(self, *args, **options):
        data = load_legislators_current()
        self.stdout.write("Got data for current legislators")
        load_data(data, self.stdout)

        data = load_legislators_past()
        self.stdout.write("Got data for past legislators")
        load_data(data, self.stdout)
