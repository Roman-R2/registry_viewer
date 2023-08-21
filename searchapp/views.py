import django
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import TemplateView

from app.settings_for_apps import REGISTRY_DATA
from authapp.mixins import IsAuthenticatedMixin, IsActiveUserMixin
from mainapp.services import get_allowed_apps, CheckSnils
from statisticapp.services import WorkWithStatistic


class IndexView(IsAuthenticatedMixin, IsActiveUserMixin, TemplateView):
    template_name = 'searchapp/main.html'

    def post(self, request: WSGIRequest, **kwargs):
        # Получим СНИЛС для поиска
        search_snils = request.POST.get('search_snils')
        # print(search_snils)

        if search_snils == '':
            return render(request, self.template_name, context={'error': 'Передан пустой СНИЛС.'})

        snils_obj = CheckSnils(search_snils)

        if not snils_obj.is_snils():
            return render(
                request,
                self.template_name,
                context={
                    'error': f'{snils_obj.get_formated_snils()}: Введенный СНИЛС не корректен. Проверьте ввод.'
                }
            )

        # Получим разрешенные пользователю приложения
        allowed_apps = get_allowed_apps(request)

        search_result = []
        search_no_snils_fields_result = []

        # Пройдем по всем приложениям, которые доступны пользователю
        for app in REGISTRY_DATA:

            if app.internal_service_registry_name not in allowed_apps:
                continue

            current_model = WorkWithStatistic.get_current_model_obj(app.internal_service_registry_name)
            search_fileds = app.fields_for_common_search.search_list_for_snils

            # Сформируем динамически запрос для ORM
            count = 0
            search_string = ''
            if search_fileds:
                for field in search_fileds:
                    if count > 0:
                        search_string += ' | '
                    search_string += f'Q({field}="{snils_obj.get_formated_snils()}")'
                    count += 1

                queryset = eval(f'current_model.objects.filter({search_string})')

                try:
                    queryset_count = queryset.count()
                except django.db.utils.ProgrammingError:
                    queryset_count = 0

                search_result.append(
                    {
                        'registry': app.long_registry_name,
                        'count': queryset_count,
                        'results': queryset.values(),
                        'app_name_string': app.internal_service_registry_name,
                    }
                )
            else:
                search_no_snils_fields_result.append(
                    {
                        'registry': app.long_registry_name,
                        'app_name_string': app.internal_service_registry_name,
                    }
                )

        return render(
            request,
            self.template_name,
            context={
                'search_snils': snils_obj.get_formated_snils(),
                'search_result': search_result,
                'search_no_snils_fields_result': search_no_snils_fields_result,
            }
        )
