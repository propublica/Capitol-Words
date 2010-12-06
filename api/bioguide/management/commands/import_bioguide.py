import csv
import sys

from django.core.management.base import BaseCommand, CommandError

from bioguide.models import Legislator

import name_tools

class Command(BaseCommand):
    def handle(self, *args, **options):
        fields = ['bioguide_id', 'name', 'birth_death', 'position', 'party', 'state', 'congress', ]
        for row in csv.reader(sys.stdin):
            row = dict(zip(fields, row))
            name = name_tools.split(row['name'])
            row['prefix'], row['first'], row['last'], row['suffix'] = name

            del(row['name'])

            print row
            legislator = Legislator.objects.create(**row)
            print legislator
