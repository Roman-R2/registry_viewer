from django.db.models import Q
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authapp.mixins import IsAuthenticatedMixin, IsActiveUserMixin
from authapp.services import get_client_ip
from statisticapp.choices import RegistryNameChoices, ActivityChoices
from statisticapp.services import WorkWithStatistic, SaveUserActivityStatistics


class MainView(IsAuthenticatedMixin, IsActiveUserMixin, TemplateView):
    template_name = 'registry_lrp/main.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # Запишем данные о том, что пользователь просматривает данный реестр

        SaveUserActivityStatistics.with_data(
            user=request.user,
            user_ip=get_client_ip(request),
            activity=ActivityChoices.USER_SHOW_REGISTRY,
            addition_data=f'Пользователь {request.user.username} просмтривает {RegistryNameChoices.REGISTRY_LRP.label} ({RegistryNameChoices.REGISTRY_LRP}).'
        )

        return self.render_to_response(context)


class RegistryLRPViewSet(IsAuthenticatedMixin, IsActiveUserMixin, mixins.ListModelMixin, GenericViewSet):
    REGISTRY_INTERNAL_NAME = 'registry_lrp'

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(queryset)

    def get_queryset(self):
        # Смещение и лимит для данных
        offset = int(self.request.GET.get('start'))
        limit = int(self.request.GET.get('length'))
        search_value = self.request.GET.get('search[value]')

        if self.request.GET.get('search_snils'):
            search_value = self.request.GET.get('search_snils')

        # Выберем модель, из которой нужно получить данные
        current_model = WorkWithStatistic.get_current_model_obj(self.REGISTRY_INTERNAL_NAME)

        # Получим набор данных запроса
        if search_value:
            queryset = current_model.objects.filter(
                Q(adult_snils=search_value) |
                Q(child_snils=search_value) |
                Q(adult_fio__icontains=search_value) |
                Q(child_fio__icontains=search_value) |
                Q(document_number=search_value)
            )
        else:
            queryset = current_model.objects.all()

        limit_queryset = queryset[offset:offset + limit]

        url_pattern = reverse('docx_generator:get_lrp_docx')

        return {
            'draw': self.request.GET.get('draw'),
            'recordsTotal': queryset.count(),
            'recordsFiltered': queryset.count(),
            'data': [
                [
                    data.adult_snils,
                    data.child_snils,
                    data.adult_fio,
                    data.child_fio,
                    data.event_type_code.code_transcript,
                    data.effective_date.strftime("%d.%m.%Y"),
                    data.series_of_document,
                    data.document_number,
                    data.issuing_authority,
                    data.document_date.strftime("%d.%m.%Y"),
                    f'<a href="{url_pattern}?snils={data.adult_snils}" type="button" class="btn btn-info btn-xs"><i class="fas fa-download fa-sm"></i><br>получить</a>'
                ]
                for data in limit_queryset]
        }
