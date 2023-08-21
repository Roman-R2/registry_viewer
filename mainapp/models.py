from django.conf import settings
from django.db import models

NULLABLE = {'null': True, 'blank': True}


class AppCanvasModel(models.Model):
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
        abstract = True
        ordering = ['-updated']


# alembic_version
class AlembicVersion(models.Model):
    """ Alembic migration check. """
    version_num = models.CharField(max_length=32)

    class Meta:
        db_table = "alembic_version"


#
# class IncludingApplications(AppCanvasModel):
#     """ Модель подключаемых приложений. """
#     # Краткое наименование приложения
#     app_short_name = models.CharField(max_length=100)
#     # Небольшое описание приложения
#     app_description = models.CharField(max_length=256)
#     # Имя приложения для генерации ссылок (app_name из urls.py)
#     app_name_string = models.CharField(max_length=50)
#     # Имяна полей для поиска по снилс
#     search_names_for_snils = models.CharField(max_length=256)
#
#     # Сопоставление приложениы и выборов RegistryNameChoices
#     # compilation_apps_and_choices = models.CharField(max_length=25)
#
#     def __str__(self):
#         return f'{self.pk} - {self.app_short_name} - {self.app_name_string}'
#
#     class Meta:
#         verbose_name = 'Подключенный реестр'
#         verbose_name_plural = 'Подключенные реестры'


class EventTypeCodes(models.Model):
    # Код
    code = models.SmallIntegerField()
    # Расшифровка кода
    code_transcript = models.CharField(max_length=1024)

    class Meta:
        verbose_name = 'Код типа события'
        verbose_name_plural = 'Коды типа события'

    def __str__(self):
        return f'Код {self.code}: {self.code_transcript}'


class AppErrorMessages(AppCanvasModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        **NULLABLE
    )
    email_for_response = models.EmailField(verbose_name="Email для ответа")
    error_message = models.TextField(verbose_name="Сообщение об ошибке")
    is_complete = models.BooleanField(default=False, verbose_name="Обработка вопроса закончена")

    class Meta:
        verbose_name = 'Сообщения об ошибках приложения'
        verbose_name_plural = 'Сообщения об ошибках приложения'
