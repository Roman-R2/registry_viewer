from django.db import models
from django.utils.translation import gettext_lazy as _


class RegistryNameChoices(models.TextChoices):
    # COMMON_RECORD = 'COMMON', _('Общая запись')
    # ------------------------- Реестры программы
    # Реестр лиц лишенных родительских прав
    REGISTRY_LRP = 'R_LRP', _('Реестр лишенных родительских прав')
    # Реестр законных представителей
    REGISTRY_ZP = 'R_ZP', _('Реестр законных представителей')
    # Реестр недееспособных
    REGISTRY_ID = 'R_ID', _('Реестр недееспособных')
    # Реестр многодетных семей
    REGISTRY_MS = 'R_MS', _('Реестр многодетных семей')
    # Реестр безработных граждан
    REGISTRY_BR = 'R_BR', _('Реестр безработных граждан')
    # Реестр Ростехнадзора по транспортным средствам
    REGISTRY_RTN_TS = 'R_RTN_TS', _('Реестр РТН ТС')
    # Реестр Ростехнадзора по транспортным средствам
    REGISTRY_STATE_SUPPORT = 'R_ST_SUPP', _('Реестр детей на гос. обеспечении')


class ErrorTypesChoices(models.TextChoices):
    COMMON_RECORD = 'COMMON', _('Общая ошибка')
    PARSE_ERROR = 'PE', _('Ошибка парсинга')


class ActivityChoices(models.TextChoices):
    LOGIN = 'LOGIN', _('Вход пользователя')
    LOGOUT = 'LOGOUT', _('Выход пользователя')
    FAILED_AUTHENTICATION = 'FAILED_AUTHENTICATION', _('Не прошел аутентификацию')
    DATA_SHOWN = 'DATA_SHOWN', _('Просмотр данных')
    PERMISSIONS_WORK = 'PERMISSIONS_WORK', _('Работа с правами на данные')
    USER_BLOCK = 'USER_BLOCK', _('Блокировка пользователя после неудачных попыток входа')
    GET_EXTRACT = 'GET_EXTRACT', _('Получение выписки из реестра')
    USER_SHOW_REGISTRY = 'USER_SHOW_REGISTRY', _('Пользователь просматривает реестр')
