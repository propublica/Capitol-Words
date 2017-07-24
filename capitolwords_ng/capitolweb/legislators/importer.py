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
    file = get_path_to_file('legislators-current.yaml')
    with open(file, 'r') as f:
        return yaml.load(f)


def load_legislators_past():
    """
    Loads the legislators-current.yaml
    :return: dict of the data
    """
    file = get_path_to_file('legislators-historical.yaml')
    with open(file, 'r') as f:
        return yaml.load(f)

