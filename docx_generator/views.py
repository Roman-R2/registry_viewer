import json
import os

from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings

from authapp.mixins import IsAuthenticatedMixin, IsActiveUserMixin
from authapp.services import get_client_ip
from docx_generator.services import AddLRPQuerysetToDocumentDotXML
from mainapp.services import CheckSnils
from statisticapp.choices import RegistryNameChoices, ActivityChoices
from statisticapp.services import WorkWithStatistic, SaveUserActivityStatistics


class GetLRPDOCX(IsAuthenticatedMixin, IsActiveUserMixin, View):
    TEMPLATE_FOLDER_PATH = os.path.join(settings.DOCX_TEMPLATE_FOLDER_PATH, r'lrp_templates\templates')
    OUTPUT_FOLDER_PATH = os.path.join(settings.DOCX_OUTPUT_FOLDER_PATH, r'lrp_docx_extract')

    # Получим текущую модель с данными
    model = WorkWithStatistic.get_current_model_obj('registry_lrp')

    def get(self, request, *args, **kwargs):
        snils = request.GET.get('snils')

        is_snils = CheckSnils(snils).is_snils()

        if not is_snils:
            return HttpResponse(
                json.dumps(
                    {'title': 'Ошибка запроса',
                     'text': 'СНИЛС не корректен'
                     }
                ),
                status=404,
                content_type="application/json"
            )

        lrp_queryset = self.model.objects.filter(
            Q(adult_snils=snils)
        )

        docx_file_folder, docx_file_name, docx_download_file_name = AddLRPQuerysetToDocumentDotXML(
            lrp_queryset).process()

        # Получим файл в виде набора байтов
        get_file_bytes = open(os.path.join(docx_file_folder, docx_file_name), "rb")
        data = get_file_bytes.read()
        get_file_bytes.close()

        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename={docx_download_file_name}'

        SaveUserActivityStatistics.with_data(
            user=request.user,
            user_ip=get_client_ip(request),
            activity=ActivityChoices.GET_EXTRACT,
            addition_data=f'Пользователь {request.user.username} получил выписку из реестра ЛРП. Файл: {docx_file_name}. Копия выписки сохранена: {docx_file_folder}'
        )

        return response
