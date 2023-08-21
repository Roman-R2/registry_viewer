from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.serializers import BackupSettingsSerializer
from mainapp.services import CheckSnils
from statisticapp.services import WorkWithStatistic


class LRPApiViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = WorkWithStatistic.get_current_model_obj(registry_name='registry_lrp')
    serializer_class = BackupSettingsSerializer
    permission_classes = [IsAuthenticated]

    request_fields = ["adult_snils", "child_snils"]

    def post(self, request, *args, **kwargs):
        if all([item in self.request.data for item in self.request_fields]):

            errors_dict = {}

            adult_snils: str = self.request.data['adult_snils']
            if adult_snils:
                is_correct_snils = CheckSnils(snils=adult_snils).is_snils()
                if not is_correct_snils:
                    errors_dict.update({'adult_snils': "Некорректный формат СНИЛС либо СНИЛС записан неправильно."})

            child_snils = self.request.data['child_snils']
            if child_snils:
                is_correct_snils = CheckSnils(snils=child_snils).is_snils()
                if not is_correct_snils:
                    errors_dict.update({'child_snils': "Некорректный формат СНИЛС либо СНИЛС записан неправильно."})

            if not adult_snils and not child_snils:
                return Response({"error": "Не заполнено ни одно из необходимых полей (adult_snils либо child_snils)"})

            if errors_dict:
                return Response(errors_dict)

            if not adult_snils and child_snils:
                data_queryset = WorkWithStatistic.get_current_model_obj(registry_name='registry_lrp').objects.filter(
                    child_snils=child_snils
                )
            elif not child_snils and adult_snils:
                data_queryset = WorkWithStatistic.get_current_model_obj(registry_name='registry_lrp').objects.filter(
                    adult_snils=adult_snils,
                )
            else:
                data_queryset = WorkWithStatistic.get_current_model_obj(registry_name='registry_lrp').objects.filter(
                    adult_snils=adult_snils,
                    child_snils=child_snils
                )

            result = []
            for item in data_queryset:
                result.append({
                    'adult_snils': item.adult_snils,
                    'child_snils': item.child_snils,
                    'adult_fio': item.adult_fio,
                    'child_fio': item.child_fio,
                    'event_type_code': item.event_type_code.code_transcript,
                    'effective_date': item.effective_date,
                    'series_of_document': item.series_of_document,
                    'document_number': item.document_number,
                    'issuing_authority': item.issuing_authority,
                    'document_date': item.document_date,
                })

            print(f"data_queryset={data_queryset}")
            return Response(
                {"lrp_data": result},
                status=status.HTTP_200_OK
            )

        return Response({"error": "Не все поля данных предоставлены"})
