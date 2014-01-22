import requests

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.conf import settings

from bioguide.models import Member, MemberRole


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
