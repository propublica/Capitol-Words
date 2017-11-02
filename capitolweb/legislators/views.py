# -*- coding: utf-8 -*-
from .models import CongressPerson, ExternalId, get_current_legislators
from rest_framework.decorators import api_view
import logging
from django.http import JsonResponse
from legislators.serializers import CongressPersonSerializer, CongressPersonShortSerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
def search_by_params(request):
    """    
    Search by query params
    supports the following ?term=val
    - id - the db id
    - name - matches against the official_full
    - last_name - last_name
    - gender
    - religion
        
    additionally supports boolean current to match only current reps

    example:
        http://127.0.0.1:8000/legislators/search/?gender=F&religion=Jewish
        http://127.0.0.1:8000/legislators/search/?gender=F&religion=Jewish&current
        
    
    :param request: 
    :return: list of CongreesPerson objects
    """

    params = request.query_params

    # if we have an id, just return it
    if 'id' in params:
        logger.info("search by id")
        return find_by_id(request, params.get('id'))

    # See if we're going with all or just current
    if 'current' in params:
        people = get_current_legislators()
    else:
        people = CongressPerson.objects
    if 'state' in params:
        logger.info("search by state")
        people = people.filter(terms__state=params.get('state'))
    if 'party' in params:
        logger.info("search by party")
        people = people.filter(terms__party=params.get('party'))
    if 'term_type' in params:
        logger.info("search by term_type")
        if params.get('term_type') in ['sen', 'rep']:
            people = people.filter(terms__type=params.get('term_type'))
    if 'name' in params:
        logger.info("search by name: " + params.get('name'))
        people = people.filter(official_full=params.get('name'))

    if 'last_name' in params:
        logger.info("search by last_name")
        people = people.filter(last=params.get('last_name'))

    if 'gender' in params:
        logger.info("search by gender")
        people = people.filter(gender=params.get('gender'))

    if 'religion' in params:
        logger.info("search by religion")
        people = people.filter(religion=params.get('religion'))

    serializer = CongressPersonSerializer(people, many=True)
    return JsonResponse(serializer.data, safe=False)


def find_by_id(request, person_id):
    """
    Find by the database id
    :param request: 
    :param person_id: the db id
    :return:  a single congress person
    """
    logger.info("Request: {}".format(person_id))
    person = CongressPerson.objects.prefetch_related('terms').get(pk=person_id)
    serializer = CongressPersonSerializer(person)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def find_by_bioguide_id(request, bioguide_id):
    """
    Return a congress person by their bioguide id
    :param request: 
    :param bioguide_id: the bioguide id
    :return:  a single CongressPerson
    """
    logger.info("Request: {}".format(bioguide_id))
    ref = ExternalId.objects.filter(type='bioguide', value=bioguide_id)[0]
    serializer = CongressPersonSerializer(ref.person)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def list_current(request):
    """
    Get all of the current CongressPeople
    :param request: optional - state=<2 letter state code>
    :return: A list of CongressPeople
    """
    params = request.query_params
    state = params.get('state', None)
    people = get_current_legislators()
    serializer = CongressPersonSerializer(people, many=True)
    return JsonResponse(serializer.data, safe=False)