from django.db import models

from mainapp.models import AppCanvasModel

NULLABLE = {'null': True, 'blank': True}


# Класс модели дополнителного реестра лишенных родительских прав
class RegistryCanvasLRPDop(AppCanvasModel):
    adult_fio = models.CharField(max_length=256)
    adult_passport_data = models.CharField(max_length=512)
    adult_registration_address = models.CharField(max_length=512)
    # Орган, выдавший документ
    issuing_authority = models.CharField(max_length=1024, **NULLABLE)
    # Дата решения
    decision_date = models.DateField(**NULLABLE)
    # Номер и дата дела
    case_number_and_date = models.CharField(max_length=1024, **NULLABLE)
    # Дата вступления решения в законную силу
    decision_entry_into_force_date = models.DateField(**NULLABLE)
    # Результат рассмотрения
    review_result = models.CharField(max_length=512)
    child_fio = models.CharField(max_length=256)
    child_birthday = models.DateField(**NULLABLE)
    # Наименование документа-основания
    name_foundation_document = models.CharField(max_length=512, **NULLABLE)
    # Реквизиты документа-основания
    details_foundation_document = models.CharField(max_length=512, **NULLABLE)

    def __str__(self):
        return f'Взрослый: {self.adult_fio} - {self.review_result}, ребенок: {self.child_fio}'

    class Meta:
        abstract = True


class RegistryLRPDopBackup1(RegistryCanvasLRPDop):
    class Meta:
        verbose_name = 'Реестр лишенных родительских прав Backup1'
        verbose_name_plural = 'Реестры лишенных родительских прав Backup1'


class RegistryLRPDopBackup2(RegistryCanvasLRPDop):
    class Meta:
        verbose_name = 'Реестр лишенных родительских прав Backup2'
        verbose_name_plural = 'Реестры лишенных родительских прав Backup2'
