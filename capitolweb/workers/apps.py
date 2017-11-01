from django.apps import AppConfig
from .tasks import scrape_crecs
from .tasks import parse_crecs

class WorkersConfig(AppConfig):
    name = 'workers'
