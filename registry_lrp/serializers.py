from rest_framework import serializers

from statisticapp.services import WorkWithStatistic


class LRPTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkWithStatistic.get_next_lrp_model_obj()
        fields = (
            'adult_snils',
            'child_snils',
            'adult_fio',
            'child_fio',
            'event_tupe_code',
            'effective_date',
            'series_of_document',
            'document_number',
            'issuing_authority',
            'document_date',
        )


class RegistryLRPBackupSerializer(serializers.Serializer):
    draw = serializers.IntegerField()
    recordsTotal = serializers.IntegerField()
    recordsFiltered = serializers.IntegerField()
    data = serializers.CharField()
