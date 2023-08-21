from django.db import models

from mainapp.models import AppCanvasModel, EventTypeCodes

NULLABLE = {'null': True, 'blank': True}


# Класс модели реестра недееспособных
class RegistryCanvasID(AppCanvasModel):
    adult_snils = models.CharField(max_length=14)
    adult_fio = models.CharField(max_length=256)
    series_of_document = models.CharField(max_length=50, **NULLABLE)
    document_number = models.CharField(max_length=70, **NULLABLE)
    # Орган, выдавший документ
    issuing_authority = models.CharField(max_length=1024, **NULLABLE)
    document_date = models.DateField()
    # Код типа события
    event_type_code = models.ForeignKey(EventTypeCodes, on_delete=models.PROTECT)
    # Дата вступления в силу
    effective_date = models.DateField()

    def __str__(self):
        return f'{self.adult_snils} - {self.adult_fio}'

    class Meta:
        abstract = True


class RegistryIDBackup1(RegistryCanvasID):
    class Meta:
        verbose_name = 'Реестр недееспособных Backup1'
        verbose_name_plural = 'Реестры недееспособных Backup1'


class RegistryIDBackup2(RegistryCanvasID):
    class Meta:
        verbose_name = 'Реестр недееспособных Backup2'
        verbose_name_plural = 'Реестры недееспособных Backup2'
