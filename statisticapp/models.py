from django.conf import settings
from django.db import models

from mainapp.models import AppCanvasModel
from statisticapp.choices import (ActivityChoices, ErrorTypesChoices,
                                  RegistryNameChoices)

NULLABLE = {'null': True, 'blank': True}


class ParseProcess(AppCanvasModel):
    """ Модель для сохранения информации о запущенном процессе автоматического парсинга данных. """
    pid = models.IntegerField(verbose_name="Pid процесса автоматического парсинга")
    name = models.CharField(max_length=50, verbose_name='Имя процесса автоматического парсинга')
    started_at = models.DateTimeField(verbose_name='Время старта процесса автоматического парсинга')

    class Meta:
        verbose_name = 'Информация о запущенных процессах автоматического парсинга данных'
        verbose_name_plural = 'Информация о запущенных процессах автоматического парсинга данных'

    def __str__(self):
        return f'Процесс автоматического парсинга pid: {self.pid}'


class StatisticAppCanvasModel(AppCanvasModel):
    """ Модель-основа. """
    registry_name = models.CharField(
        max_length=50
    )

    class Meta:
        abstract = True


class ParserErrors(StatisticAppCanvasModel):
    """ Модель для ошибок парсинга регистров. """

    error_type = models.CharField(
        max_length=30,
        choices=ErrorTypesChoices.choices,
        default=ErrorTypesChoices.PARSE_ERROR,
        verbose_name='Тип ошибки',
    )
    error_message = models.TextField(verbose_name='Текст ошибки', **NULLABLE)
    addition_data = models.TextField(
        verbose_name='Дополнительная информация',
        **NULLABLE
    )

    class Meta:
        verbose_name = 'Ошибки парсинга данных'
        verbose_name_plural = 'Ошибки парсинга данных'

    def __str__(self):
        return f'Ошибка {self.registry_name}: {self.error_type}. {self.created_at}'


class ParseFileStat(AppCanvasModel):
    # Полный путь до файла
    file_path = models.TextField(verbose_name='Полный путь до файла')
    last_access_time = models.DateTimeField(verbose_name='Время последнего доступа. (access)')
    last_modify_time = models.DateTimeField(verbose_name='Время последней модификации контента. (modify)')
    last_create_time = models.DateTimeField(verbose_name='Время создания. (create)')

    class Meta:
        verbose_name = 'Данные файлов регистров, которые были собраны'
        verbose_name_plural = 'Данные файлов регистров, которые были собраны'

    def __str__(self):
        return f'Собранный файл {self.file_path}'


class ParseStatistics(StatisticAppCanvasModel):
    """ Модель для статистики парсинга регистров. """
    file = models.ForeignKey(to=ParseFileStat, on_delete=models.CASCADE, verbose_name='Файл, который был собран')
    parse_start_date = models.DateTimeField(verbose_name='Время старта парсинга')
    parse_end_date = models.DateTimeField(verbose_name='Время окончания парсинга')
    parse_model_name = models.CharField(max_length=50, verbose_name='Модель прсинга')
    parse_number_of_lines = models.IntegerField(verbose_name='Количество внесеных записей')
    parse_process_count = models.IntegerField(verbose_name='Порядковый номер парсинга')

    class Meta:
        verbose_name = 'Статистика парсинга данных'
        verbose_name_plural = 'Статистика парсинга данных'

    def __str__(self):
        return f'{self.parse_model_name}: {self.parse_number_of_lines} строк. Счетчик: {self.parse_process_count}'


class UserActivityStatistics(AppCanvasModel):
    """ Модель для статистики по аворизациям, выходам и другим действиям в приложении. """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        **NULLABLE
    )
    user_ip = models.CharField(
        max_length=30,
        default='0.0.0.0',
        verbose_name='IP адрес пользователя',
    )
    activity = models.CharField(
        max_length=30,
        choices=ActivityChoices.choices,
        default=ActivityChoices.LOGIN,
        verbose_name='Тип активности пользователя',
    )
    addition_data = models.TextField(verbose_name='Дополнительная информация')

    class Meta:
        verbose_name = 'Статистика по активности пользователя'
        verbose_name_plural = 'Статистика по активностям пользователя'

    def __str__(self):
        return f'{self.user}: {self.activity} - {self.created_at}'


class UserFailedLoginAttempts(AppCanvasModel):
    """ Модель для статистики по неудачным попыткам входа пользователей. """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    number_of_failed_attempts = models.SmallIntegerField(
        default=0,
        verbose_name='Колличество неуданчых попыток входа',
    )
    expired_date = models.DateTimeField(
        **NULLABLE,
        verbose_name='Дата истечения блокировки'
    )

    class Meta:
        verbose_name = 'Статистика по по неудачным попыткам входа пользователей'
        verbose_name_plural = 'Статистика по по неудачным попыткам входа пользователей'

    def __str__(self):
        return f'{self.user}: {self.user} - {self.number_of_failed_attempts}'
