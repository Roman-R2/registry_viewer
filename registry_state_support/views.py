from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, FormView
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authapp.mixins import IsAuthenticatedMixin, IsActiveUserMixin
from authapp.services import get_client_ip
from registry_state_support.forms import StateSupportForm
from statisticapp.choices import RegistryNameChoices, ActivityChoices
from statisticapp.services import WorkWithStatistic, SaveUserActivityStatistics


class MainView(IsAuthenticatedMixin, IsActiveUserMixin, TemplateView):
    template_name = 'registry_state_support/main.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # Запишем данные о том, что пользователь просматривает данный реестр
        SaveUserActivityStatistics.with_data(
            user=request.user,
            user_ip=get_client_ip(request),
            activity=ActivityChoices.USER_SHOW_REGISTRY,
            addition_data=f'Пользователь {request.user.username} просмтривает {RegistryNameChoices.REGISTRY_STATE_SUPPORT.label} ({RegistryNameChoices.REGISTRY_STATE_SUPPORT}).'
        )

        return self.render_to_response(context)


class RegistryStateSupportViewSet(IsAuthenticatedMixin, IsActiveUserMixin, mixins.ListModelMixin, GenericViewSet):
    REGISTRY_INTERNAL_NAME = 'registry_state_support'

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
                Q(adult_fio__icontains=search_value) |
                Q(child_snils=search_value) |
                Q(child_fio__icontains=search_value) |
                Q(another_adult_snils=search_value) |
                Q(another_adult_fio__icontains=search_value)
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
                    data.adult_snils,
                    data.adult_fio,
                    data.child_snils,
                    data.child_fio,
                    data.child_birthdate.strftime("%d.%m.%Y"),
                    data.child_start_support_date.strftime("%d.%m.%Y"),
                    data.child_location,
                    data.child_status,
                    data.another_adult_snils,
                    data.another_adult_fio,
                ]
                for data in limit_queryset]
        }


class StateSupportFormView(IsAuthenticatedMixin, IsActiveUserMixin, FormView):
    template_name = 'registry_state_support/add_row_form.html'
    form_class = StateSupportForm
    success_url = reverse_lazy("registry_state_support:index")

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()
            return render(
                request,
                self.template_name,
                {'form': self.form_class(), 'success_saved_form': True}
            )
        else:
            return render(
                request,
                self.template_name,
                {'form': form}
            )

    #
    # def get(self, request, *args, **kwargs):
    #     form = self.form_class()
    #     return render(request, self.success_url, {'form': form})
    #
    def get(self, request, *args, **kwargs):
        # print(self.form_class().fields['adult_snils'].__dict__)
        return super().get(self, request, *args, **kwargs)
