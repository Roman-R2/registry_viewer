from django.db import models

from mainapp.models import AppCanvasModel

NULLABLE = {'null': True, 'blank': True}


# Класс модели безработных лиц
class RegistryCanvasBR(AppCanvasModel):
    fio = models.CharField(max_length=256)  # Фамилия, Имя, Отчество
    date_of_birth = models.DateField()  # Дата рождения
    snils = models.CharField(max_length=14, **NULLABLE)  # СНИЛС
    division = models.CharField(max_length=256)  # Подразделение
    adress = models.TextField(**NULLABLE)  # Адрес проживания гражданина
    phones = models.CharField(max_length=512)  # Телефоны гражданина
    date_of_initial_appeal = models.DateField()  # Дата первичного обращения
    date_registration_as_unemployed = models.DateField(**NULLABLE)  # Дата признания безработным
    payment_start_date = models.DateField()  # Дата начала выплаты
    payment_end_date = models.DateField()  # Дата окончания выплаты
    name_of_the_payment = models.CharField(max_length=256)  # Наименование выплаты
    date_de_registration_as_unemployed = models.DateField(**NULLABLE)  # Дата снятия с учета в качестве безработного
    date_start_billing_period = models.DateField(**NULLABLE)  # Начисления - Дата начала расчетного периода
    date_end_billing_period = models.DateField(**NULLABLE)  # Начисления - Дата окончания расчетного периода
    amount_accrued = models.FloatField(**NULLABLE)  # Начисления - Сумма начисленная

    def __str__(self):
        return f'Безработный: {self.fio} - {self.snils}, {self.date_of_birth} г.р.'

    class Meta:
        abstract = True


class RegistryBRBackup1(RegistryCanvasBR):
    class Meta:
        verbose_name = 'Реестр многодетных семей Backup1'
        verbose_name_plural = 'Реестры многодетных семей Backup1'


class RegistryBRBackup2(RegistryCanvasBR):
    class Meta:
        verbose_name = 'Реестр многодетных семей Backup2'
        verbose_name_plural = 'Реестры многодетных семей Backup2'
