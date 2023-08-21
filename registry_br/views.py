from django.db.models import Q
from django.views.generic import TemplateView
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authapp.mixins import IsAuthenticatedMixin, IsActiveUserMixin
from authapp.services import get_client_ip
from statisticapp.choices import RegistryNameChoices, ActivityChoices
from statisticapp.services import WorkWithStatistic, SaveUserActivityStatistics


class MainView(IsAuthenticatedMixin, IsActiveUserMixin, TemplateView):
    template_name = 'registry_br/main.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # Запишем данные о том, что пользователь просматривает данный реестр

        SaveUserActivityStatistics.with_data(
            user=request.user,
            user_ip=get_client_ip(request),
            activity=ActivityChoices.USER_SHOW_REGISTRY,
            addition_data=f'Пользователь {request.user.username} просмтривает {RegistryNameChoices.REGISTRY_BR.label} ({RegistryNameChoices.REGISTRY_BR}).'
        )

        return self.render_to_response(context)


class RegistryBRViewSet(IsAuthenticatedMixin, IsActiveUserMixin, mixins.ListModelMixin, GenericViewSet):
    REGISTRY_INTERNAL_NAME = 'registry_br'

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
                Q(snils=search_value) |
                Q(fio__icontains=search_value)
            )
        else:
            queryset = current_model.objects.all()

        limit_queryset = queryset[offset:offset + limit]
        return {
            'draw': self.request.GET.get('draw'),
            'recordsTotal': queryset.count(),
            'recordsFiltered': queryset.count(),
            'data': [
                [
                    data.fio,
                    data.snils if data.snils else '-',
                    data.date_of_birth.strftime("%d.%m.%Y"),
                    data.adress,
                    data.date_of_initial_appeal.strftime("%d.%m.%Y"),
                    data.date_registration_as_unemployed,
                    data.payment_start_date.strftime("%d.%m.%Y") if data.payment_start_date else '-',
                    data.payment_end_date.strftime("%d.%m.%Y") if data.payment_end_date else '-',
                    data.name_of_the_payment,
                    data.date_de_registration_as_unemployed if data.date_de_registration_as_unemployed else '-',
                    data.date_start_billing_period if data.date_start_billing_period else '-',
                    data.date_end_billing_period if data.date_end_billing_period else '-',
                    data.amount_accrued if data.amount_accrued else '-',
                    data.phones,
                    data.division,
                ]
                for data in limit_queryset]
        }
