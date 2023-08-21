from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView, RedirectView

from authapp.mixins import (IsActiveUserMixin, IsAuthenticatedMixin,
                            IsStaffUserMixin)
from authapp.models import AppExtendedUser
from mainapp.models import AppErrorMessages


class IndexView(IsAuthenticatedMixin, IsActiveUserMixin, TemplateView):
    template_name = 'mainapp/registrys.html'


class StoreErrorMessageToDB(IsAuthenticatedMixin, IsActiveUserMixin, TemplateView):
    template_name = 'mainapp/send_app_error_message.html'

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        context['is_post_action'] = True

        email_field = self.request.POST.get('email_field', None).strip()
        message_field = self.request.POST.get('message_field', None).strip()

        if email_field is not None:
            context['message_about_email'] = f'Вы указали {email_field} для ответа на обращение.'
        if message_field is not None:
            AppErrorMessages.objects.create(
                user=request.user,
                email_for_response=email_field,
                error_message=message_field
            )
            context['is_app_send_message'] = True
        else:
            context['is_app_send_message'] = False
            context['send_error'] = 'Вы отправили пустое сообщение'

        return self.render_to_response(context)
