from pprint import pprint

from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db import IntegrityError
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import DeleteView, TemplateView
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.settings_for_apps import REGISTRY_DATA
from authapp.forms import AppExtendedUserLoginForm, AppExtendedUserRegisterForm
from authapp.mixins import (IsActiveUserMixin, IsAuthenticatedMixin,
                            IsStaffUserMixin)
from authapp.models import AppExtendedUser, UserAllowedApps
from authapp.services import check_next_in_request, get_client_ip
from mainapp.services import permission_denied_403, user_blocked_403
from statisticapp.choices import ActivityChoices
from statisticapp.services import (SaveUserActivityStatistics,
                                   WorkUserFailedLoginAttempts)


def login(request):
    login_form = AppExtendedUserLoginForm(data=request.POST)
    next_url = request.GET.get('next', '')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        # Если пользователь заблокирован, то покажем это
        if WorkUserFailedLoginAttempts.is_blocked_user(username):
            return user_blocked_403(request)

        if login_form.is_valid():
            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                auth.login(request, user)

                # Запись об успешном входе
                SaveUserActivityStatistics.with_data(
                    user=user,
                    user_ip=get_client_ip(request),
                    activity=ActivityChoices.LOGIN,
                    addition_data=f'Вход пользователя в приложение: username={username}'
                )

                # Сбросим счетчик неудачных попыток входа
                WorkUserFailedLoginAttempts.reset_login_attempts(user=user)

                if check_next_in_request(request):
                    return HttpResponseRedirect(request.POST['next'])
                return HttpResponseRedirect(reverse('mainapp:index'))

        else:
            user = WorkUserFailedLoginAttempts.get_user_or_none(username)

            # Запись о неудачной попытке входа в приложении, если имя пользователя найдено в БД
            WorkUserFailedLoginAttempts.with_data(
                user_name=username
            )

            # Запись о неудачной аутентификации
            SaveUserActivityStatistics.with_data(
                user=user,
                user_ip=get_client_ip(request),
                activity=ActivityChoices.FAILED_AUTHENTICATION,
                addition_data=f'Пользователь не прошел аутентификацию: username={username}'
            )

            context = {
                'login_form': login_form,
                'next': next_url,
            }

            return render(request, 'authapp/login.html', context=context)
    else:
        context = {
            'login_form': login_form,
            'next': next_url,
        }

        return render(request, 'authapp/login.html', context=context)


def logout(request):
    # Запись о выходе из приложения
    SaveUserActivityStatistics.with_data(
        user=request.user,
        user_ip=get_client_ip(request),
        activity=ActivityChoices.LOGOUT,
        addition_data=f'Выход пользователя из приложения: {request.user.username}'
    )
    auth.logout(request)
    return HttpResponseRedirect(reverse('authapp:login'))


def register(request: WSGIRequest):
    if (request.user.is_superuser or request.user.is_staff) and request.user.is_active:

        if request.method == 'POST':
            register_form = AppExtendedUserRegisterForm(request.POST, request.FILES)
            if register_form.is_valid():
                saved_user = register_form.save()

                SaveUserActivityStatistics.with_data(
                    user=request.user,
                    user_ip=get_client_ip(request),
                    activity=ActivityChoices.PERMISSIONS_WORK,
                    addition_data=f'Новый пользователь {request.POST.get("username")} зарегистрирован. Регистрацию произвел: {request.user.username}'
                )

                return HttpResponseRedirect(reverse('authapp:permissions_user', kwargs={'pk': saved_user.pk}))
        else:
            register_form = AppExtendedUserRegisterForm()
        context = {
            "register_form": register_form,
        }

    else:
        return permission_denied_403(request)

    return render(request, 'authapp/register.html', context=context)


class ActiveUsers(IsAuthenticatedMixin, IsStaffUserMixin, IsActiveUserMixin, TemplateView):
    template_name = 'authapp/users.html'


class NotActiveUsers(IsAuthenticatedMixin, IsStaffUserMixin, IsActiveUserMixin, TemplateView):
    template_name = 'authapp/not_active_users.html'


class DeleteAppExtendedUser(IsAuthenticatedMixin, IsStaffUserMixin, IsActiveUserMixin, DeleteView):
    model = AppExtendedUser
    template_name = 'authapp/user_delete.html'
    success_url = reverse_lazy('authapp:users')

    def get(self, request, **kwargs):
        delete_user = get_object_or_404(AppExtendedUser, pk=kwargs['pk'])
        # Не дадим удалить себя
        if request.user == delete_user:
            return permission_denied_403(request)
        # Не дадим удалить персоналу персонала или администратора
        if request.user.is_staff and not request.user.is_superuser:
            if delete_user.is_superuser or delete_user.is_staff:
                return permission_denied_403(request)
        return super().get(request, **kwargs)

    def delete(self, request, **kwargs):
        delete_user = get_object_or_404(AppExtendedUser, pk=kwargs['pk'])
        # Не дадим удалить себя
        if request.user == delete_user:
            return permission_denied_403(request)
        # Не дадим удалить персоналу персонала или администратора
        if request.user.is_staff and not request.user.is_superuser:
            if delete_user.is_superuser or delete_user.is_staff:
                return permission_denied_403(request)

        SaveUserActivityStatistics.with_data(
            user=request.user,
            user_ip=get_client_ip(request),
            activity=ActivityChoices.PERMISSIONS_WORK,
            addition_data=f'Пользователь {delete_user.username} удален. Удаление произвел: {request.user.username}'
        )
        return super().delete(request, **kwargs)


class RefreshAppExtendedUser(IsAuthenticatedMixin, IsStaffUserMixin, IsActiveUserMixin, TemplateView):
    template_name = 'authapp/user_refresh.html'

    def get_context_data(self, **kwargs):
        return {
            'object': AppExtendedUser.objects.filter(pk=kwargs['pk']).first()
        }

    def get(self, request, **kwargs):
        refresh_user = get_object_or_404(AppExtendedUser, pk=kwargs['pk'])
        # Не дадим восстановить себя
        if request.user == refresh_user:
            return permission_denied_403(request)
        # Не дадим восстановить персоналу персонала или администратора
        if request.user.is_staff and not request.user.is_superuser:
            if refresh_user.is_superuser or refresh_user.is_staff:
                return permission_denied_403(request)
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        refresh_user = get_object_or_404(AppExtendedUser, pk=kwargs['pk'])

        # Не дадим восстановить себя
        if request.user == refresh_user:
            return permission_denied_403(request)
        # Не дадим восстановить персоналу персонала или администратора
        if request.user.is_staff and not request.user.is_superuser:
            if refresh_user.is_superuser or refresh_user.is_staff:
                return permission_denied_403(request)

        refresh_user.is_active = True
        refresh_user.save()

        SaveUserActivityStatistics.with_data(
            user=request.user,
            user_ip=get_client_ip(request),
            activity=ActivityChoices.PERMISSIONS_WORK,
            addition_data=f'Пользователь {refresh_user.username} восстановлен. Изменения произвел: {request.user.username}'
        )
        return HttpResponseRedirect(reverse('authapp:not_active_users'))


class PermissionsAppExtendedUser(IsAuthenticatedMixin, IsStaffUserMixin, IsActiveUserMixin, TemplateView):
    template_name = 'authapp/user_permissions.html'

    def get_context_data(self, **kwargs):
        target_user = AppExtendedUser.objects.filter(pk=kwargs['pk']).first()

        try:
            user_permissions = UserAllowedApps.objects.get(user=target_user)
        except ObjectDoesNotExist:
            user_permissions = UserAllowedApps.objects.create(user=target_user)

        if 'changed' in kwargs:
            is_changed = True
        else:
            is_changed = False

        user_permissions_dict = model_to_dict(user_permissions)

        permissions = []
        for app in REGISTRY_DATA:
            permissions.append((app, user_permissions_dict[app.internal_service_registry_name]))

        return {
            'target_user': target_user,
            'permissions': permissions,
            'is_changed': is_changed
        }

    def get(self, request, **kwargs):
        target_user = get_object_or_404(AppExtendedUser, pk=kwargs['pk'])
        # Не дадим восстановить себя
        if request.user == target_user:
            return permission_denied_403(request)
        # Не дадим восстановить персоналу персонала или администратора
        if request.user.is_staff and not request.user.is_superuser:
            if target_user.is_superuser or target_user.is_staff:
                return permission_denied_403(request)
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        target_user = AppExtendedUser.objects.filter(pk=kwargs['pk']).first()
        # including_applications = IncludingApplications.objects.all()
        try:
            user_permissions = UserAllowedApps.objects.filter(user=target_user)
        except:
            HttpResponse('No!')

        # Не дадим изменить даные себе
        if request.user == target_user:
            return permission_denied_403(request)
        # Не дадим изменить даные персоналу персонала или администратора
        if request.user.is_staff and not request.user.is_superuser:
            if target_user.is_superuser or target_user.is_staff:
                return permission_denied_403(request)

        # Соберем словарь новых разрешений на данные
        new_permissions = {}
        for app in REGISTRY_DATA:
            try:
                if request.POST[app.internal_service_registry_name] == 'on':
                    new_permissions[app.internal_service_registry_name] = True
            except MultiValueDictKeyError:
                new_permissions[app.internal_service_registry_name] = False

        # Изменим значения
        user_permissions.update(**new_permissions)

        SaveUserActivityStatistics.with_data(
            user=request.user,
            user_ip=get_client_ip(request),
            activity=ActivityChoices.PERMISSIONS_WORK,
            addition_data=f'У пользователя {target_user.username} изменились права на данные. Изменения внес: {request.user.username}. Права: {new_permissions}'
        )

        kwargs.update({'changed': 'yes'})

        response = render(
            request,
            'authapp/user_permissions.html',
            context=self.get_context_data(**kwargs)
        )
        response['Changed'] = 'True'
        return response


class UserJSONViewSet(IsAuthenticatedMixin, IsActiveUserMixin, mixins.ListModelMixin, GenericViewSet):

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(queryset)

    def get_queryset(self):

        if self.request.GET.get('not_active_users') == 'true':
            IS_ACTIVE_USERS = False
        else:
            IS_ACTIVE_USERS = True

        yes_checker = '<span style="font-size: 1.5em; color: green;"><i class="fas fa-check-circle"></i></span>'
        no_checker = '<span style="font-size: 1.5em; color: red;"><i class="fas fa-times-circle"></i></span>'

        CURRENT_USER_PK = self.request.user.pk

        if self.request.user.is_superuser:
            IS_SUPERUSER = True
        else:
            IS_SUPERUSER = False

        if not self.request.user.is_superuser and self.request.user.is_staff:
            ONLY_STAFF = True
        else:
            ONLY_STAFF = False

        if IS_ACTIVE_USERS:
            url_pattern = reverse('authapp:delete_user', args=('user_pk',))
            url_pattern = url_pattern.replace('user_pk', '{user_pk}')

            url_permission_pattern = reverse('authapp:permissions_user', args=('user_pk',))
            url_permission_pattern = url_permission_pattern.replace('user_pk', '{user_pk}')

            delete_user = f'<a href="{url_pattern}"><button type="button" class="btn btn-danger btn-sm"><i class="fas fa-trash-alt fa-sm"></i></button></a>'
            edit_data_sources = f'<a href="{url_permission_pattern}"><button type="button" class="btn btn-info btn-sm"><i class="fas fa-inbox fa-sm"></i></button></a>'

            admin_buttons = '<nobr>' + edit_data_sources + '&nbsp;' + delete_user + '</nobr>'

        else:
            url_pattern = reverse('authapp:refresh_user', args=('user_pk',))
            url_pattern = url_pattern.replace('user_pk', '{user_pk}')

            admin_buttons = f'<a href="{url_pattern}"><button type="button" class="btn btn-info btn-sm"><i class="fas fa-redo fa-sm"></i></button></a>'

        # Смещение и лимит для данных
        offset = int(self.request.GET.get('start'))
        limit = int(self.request.GET.get('length'))
        search_value = self.request.GET.get('search[value]')

        # Выберем модель, из которой нужно получить данные
        current_model = AppExtendedUser

        # Получим набор данных запроса
        if search_value:
            queryset = current_model.objects.filter(
                Q(first_name__icontains=search_value) |
                Q(last_name__icontains=search_value) |
                Q(username__icontains=search_value),
                is_active=IS_ACTIVE_USERS
            )
        else:
            queryset = current_model.objects.filter(is_active=IS_ACTIVE_USERS)

        limit_queryset = queryset[offset:offset + limit]
        return {
            'draw': self.request.GET.get('draw'),
            'recordsTotal': queryset.count(),
            'recordsFiltered': queryset.count(),
            'data': [
                [
                    (
                        admin_buttons.format(user_pk=data.pk)
                    ) if (IS_SUPERUSER or (
                            ONLY_STAFF and not data.is_superuser and not data.is_staff
                    )) and not (CURRENT_USER_PK == data.pk) else '',
                    f'<b>{data.username}</b>',
                    data.last_name if data.last_name else '-',
                    data.first_name if data.first_name else '-',
                    data.patronymic if data.patronymic else '-',
                    data.office if data.office else '-',
                    yes_checker if data.is_superuser else no_checker,
                    yes_checker if data.is_staff else no_checker,
                    yes_checker if data.is_active else no_checker,
                ]
                for data in limit_queryset]
        }
