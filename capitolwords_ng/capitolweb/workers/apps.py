from django.apps import AppConfig
from .tasks import scrape_crecs

class WorkersConfig(AppConfig):
    name = 'workers'
