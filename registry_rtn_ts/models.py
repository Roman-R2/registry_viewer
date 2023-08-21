from django.db import models

from mainapp.models import AppCanvasModel

NULLABLE = {'null': True, 'blank': True}


# Класс модели безработных лиц
class RegistryCanvasRtnTs(AppCanvasModel):
    fio = models.CharField(max_length=512)  # Фамилия, Имя, Отчество
    date_of_birth = models.DateField(**NULLABLE)  # Дата рождения
    ts_name = models.CharField(max_length=1024)  # Наименование транспортного средства
    ts_year_of_construct = models.CharField(max_length=128)  # Год выпуска транспортного средства

    def __str__(self):
        return f'Владелец ТС: {self.fio}, {self.date_of_birth} г.р. - {self.ts_name} ({self.ts_year_of_construct})'

    class Meta:
        abstract = True


class RegistryRtnTsBackup1(RegistryCanvasRtnTs):
    class Meta:
        verbose_name = 'Реестр Ростехнадзора по транспортным средствам Backup1'
        verbose_name_plural = 'Реестр Ростехнадзора по транспортным средствам Backup1'


class RegistryRtnTsBackup2(RegistryCanvasRtnTs):
    class Meta:
        verbose_name = 'Реестр Ростехнадзора по транспортным средствам Backup2'
        verbose_name_plural = 'Реестр Ростехнадзора по транспортным средствам Backup2'
