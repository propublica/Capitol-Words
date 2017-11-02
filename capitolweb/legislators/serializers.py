from rest_framework import serializers
from legislators.models import Term, CongressPerson, ExternalId


class TermSerializer(serializers.ModelSerializer):

    class Meta:
        model = Term
        fields = ('type', 'start_date', 'end_date', 'state', 'district', 'party', 'election_class',
                  'state_rank', 'caucus')


class ExternalIdSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExternalId
        fields = ('type', 'value')


class CongressPersonSerializer(serializers.ModelSerializer):
    terms = TermSerializer(many=True)
    external_ids = ExternalIdSerializer(many=True)

    class Meta:
        model = CongressPerson
        fields = ('bioguide_id', 'first', 'middle', 'last', 'suffix', 'nickname', 'official_full', 'birthday',
                  'gender', 'religion', 'terms', 'external_ids', 'image_lg', 'image_sm',)


class CongressPersonShortSerializer(serializers.ModelSerializer):
    terms = TermSerializer(many=True)

    class Meta:
        model = CongressPerson
        fields = ('bioguide_id', 'first', 'middle', 'last', 'suffix', 'official_full', 'birthday',
                  'gender', 'religion', 'terms', 'image_lg', 'image_sm',)


