from django import forms
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

NULLABLE = {'null': True, 'blank': True}


class AppExtendedUser(AbstractUser):
    # Переопределил, чтобы поля нельзя было оставить пустыми
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    password = models.CharField(_('password'), max_length=128)

    # Отчество
    patronymic = models.CharField(
        max_length=124,
        verbose_name='Отчество',
        **NULLABLE
    )
    # Должность
    office = models.CharField(
        max_length=124,
        verbose_name='Должность',
        **NULLABLE
    )
    # Метка того, что пользователю доспупны данные для внутренней работы
    # is_own_people = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class UserAllowedApps(models.Model):
    """ Модель приложений (реестров), доступных пользователям """
    # Метка доступности реестра ЛРП
    registry_lrp = models.BooleanField(
        default=False,
        verbose_name='Доступность реестра ЛРП',
    )
    # Метка доступности реестра инвалидов
    registry_id = models.BooleanField(
        default=False,
        verbose_name='Доступность реестра недееспособных',
    )
    # Метка доступности реестра законных представителей
    registry_zp = models.BooleanField(
        default=False,
        verbose_name='Доступность реестра законных представителей',
    )
    # Метка доступности реестра многодетных семей
    registry_ms = models.BooleanField(
        default=False,
        verbose_name='Доступность реестра многодетных семей',
    )
    # Метка доступности реестра многодетных семей
    registry_br = models.BooleanField(
        default=False,
        verbose_name='Доступность реестра безработных граждан',
    )
    # Метка доступности реестра Ростехнадзора по транспортным средствам
    registry_rtn_ts = models.BooleanField(
        default=False,
        verbose_name='Доступность реестра Ростехнадзора по транспортным средствам',
    )
    # Метка доступности дополнительного реестра ЛРП
    registry_lrp_dop = models.BooleanField(
        default=False,
        verbose_name='Доступность дополнительного реестра ЛРП',
    )
    # Метка доступности реестра детей на гособеспечении
    registry_state_support = models.BooleanField(
        default=False,
        verbose_name='Доступность реестра детей на гособеспечении',
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано',
        editable=False,
        null=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено',
        editable=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Права на данные'
        verbose_name_plural = 'Права на данные'

    def __str__(self):
        return f'Разрешения для {self.user.username}'
