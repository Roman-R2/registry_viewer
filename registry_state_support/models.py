from django.db import models

from mainapp.models import AppCanvasModel, EventTypeCodes

NULLABLE = {'null': True, 'blank': True}


# Класс модели реестра детей на гособеспечении
class RegistryCanvasStateSupport(AppCanvasModel):
    # СНИЛС взрослого
    adult_snils = models.CharField(max_length=14, verbose_name='СНИЛС взрослого')
    # ФИО взрослого
    adult_fio = models.CharField(max_length=256, verbose_name='ФИО взрослого')
    # СНИЛС ребенка
    child_snils = models.CharField(max_length=14, verbose_name='СНИЛС ребенка')
    # ФИО ребенка
    child_fio = models.CharField(max_length=256, verbose_name='ФИО ребенка')
    # Дата рождения ребенка
    child_birthdate = models.DateField(verbose_name='Дата рождения ребенка')
    # Дата поступления на гос. обеспечение
    child_start_support_date = models.DateField(verbose_name='Дата поступления на гос. обеспечение')
    # Место нахождения ребенка
    child_location = models.CharField(max_length=256, verbose_name='Место нахождения ребенка', **NULLABLE)
    # Статус ребенка
    child_status = models.CharField(max_length=256, verbose_name='Статус ребенка на гос. обеспечении', **NULLABLE)
    # СНИЛС другого родителя/законного представителя
    another_adult_snils = models.CharField(
        max_length=14,
        verbose_name='СНИЛС другого родителя/законного представителя',
        **NULLABLE
    )
    # ФИО другого родителя/законного представителя
    another_adult_fio = models.CharField(
        max_length=256,
        verbose_name='ФИО другого родителя/законного представителя',
        **NULLABLE
    )

    def __str__(self):
        return f'Взрослый: {self.adult_snils} - {self.adult_fio}, ребенок: {self.child_snils} - {self.child_fio}'

    class Meta:
        abstract = True


class RegistryStateSupportBackup1(RegistryCanvasStateSupport):
    class Meta:
        verbose_name = 'Реестр детей на гособеспечении Backup1'
        verbose_name_plural = 'Реестры детей на гособеспечении Backup1'


class RegistryStateSupportBackup2(RegistryCanvasStateSupport):
    class Meta:
        verbose_name = 'Реестр детей на гособеспечении Backup2'
        verbose_name_plural = 'Реестры детей на гособеспечении Backup2'
