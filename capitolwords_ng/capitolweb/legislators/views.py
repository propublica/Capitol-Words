# -*- coding: utf-8 -*-
from .models import CongressPerson, ExternalId, get_current_legislators
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
import logging
from django.http import HttpResponse, JsonResponse
from legislators.serializers import CongressPersonSerializer, CongressPersonShortSerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
def find_by_name(request, name):
    people = CongressPerson.objects.prefetch_related('terms').filter(official_full__icontains=name)
    serializer = CongressPersonSerializer(people, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def find_by_id(request, person_id):
    logger.info("Request: {}".format(person_id))

    people = CongressPerson.objects.prefetch_related('terms').get(pk=person_id)
    serializer = CongressPersonSerializer(people)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def find_by_bioguide_id(request, bioguide_id):
    logger.info("Request: {}".format(bioguide_id))
    ref = ExternalId.objects.filter(type='bioguide', value=bioguide_id)[0]
    serializer = CongressPersonSerializer(ref.person)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def list_current(request):
    logger.info("Request: {}".format(request.query_params.get('foo')))
    params = request.query_params
    state = params.get('state', None)
    people = get_current_legislators(state=state)
    serializer = CongressPersonShortSerializer(people, many=True)
    return JsonResponse(serializer.data, safe=False)