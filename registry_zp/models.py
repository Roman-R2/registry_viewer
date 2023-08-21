
from django.db import models

from mainapp.models import AppCanvasModel, EventTypeCodes

NULLABLE = {'null': True, 'blank': True}


# Класс модели реестра законных представителей
class RegistryCanvasZP(AppCanvasModel):
    adult_snils = models.CharField(max_length=14)
    child_snils = models.CharField(max_length=14)
    adult_fio = models.CharField(max_length=256)
    child_fio = models.CharField(max_length=256)
    # Код типа события
    event_type_code = models.ForeignKey(EventTypeCodes, on_delete=models.PROTECT)
    # Дата вступления в силу
    effective_date = models.DateField()
    series_of_document = models.CharField(max_length=50, **NULLABLE)
    document_number = models.CharField(max_length=70, **NULLABLE)
    # Орган, выдавший документ
    issuing_authority = models.CharField(max_length=1024, **NULLABLE)
    document_date = models.DateField()

    def __str__(self):
        return f'Взрослый: {self.adult_snils} - {self.adult_fio}, ребенок: {self.child_snils} - {self.child_fio}'

    class Meta:
        abstract = True


class RegistryZPBackup1(RegistryCanvasZP):
    class Meta:
        verbose_name = 'Реестр законных представителей Backup1'
        verbose_name_plural = 'Реестры законных представителей Backup1'


class RegistryZPBackup2(RegistryCanvasZP):
    class Meta:
        verbose_name = 'Реестр законных представителей Backup2'
        verbose_name_plural = 'Реестры законных представителей Backup2'
