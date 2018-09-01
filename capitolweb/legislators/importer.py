import requests
import yaml
import os

DATA_DIR = 'external_data'


def get_path_to_file(yaml_file):
    return "{}/{}/{}".format(os.getcwd(), DATA_DIR, yaml_file)

def load_legislators_current():
    """
    Loads the legislators-current.yaml
    :return: dict of the data
    """
    response = requests.get('https://theunitedstates.io/congress-legislators/legislators-current.yaml')
    return yaml.load(response.content)

def load_legislators_past():
    """
    Loads the legislators-current.yaml
    :return: dict of the data
    """
    response = requests.get('https://theunitedstates.io/congress-legislators/legislators-historical.yaml')
    return yaml.load(response.content)
