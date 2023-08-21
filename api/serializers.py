from abc import ABC

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.serializers import (ModelSerializer, Serializer)

from statisticapp.services import WorkWithStatistic


class BackupSettingsSerializer(ModelSerializer):
    class Meta:
        model = WorkWithStatistic.get_current_model_obj(registry_name='registry_lrp')
        fields = [
            'adult_snils',
            'child_snils',
            'adult_fio',
            'child_fio',
            'event_type_code',
            'effective_date',
            'series_of_document',
            'document_number',
            'issuing_authority',
            'document_date',
        ]