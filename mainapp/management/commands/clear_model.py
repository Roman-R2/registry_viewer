"""
Команда для добавления приложений в модель IncludingApplications
"""
from django.apps import apps
from django.core.management import BaseCommand

from mainapp.services import RebuildDataParseModel


class Command(BaseCommand):
    help = 'Полностью очистит таблицу в БД по переданному имени модели'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_name',
            type=str,
            help='Имя приложения в котором находится таблица.'
        )

        parser.add_argument(
            'model_name',
            type=str,
            help='Имя модели для очистки таблицы.'
        )

    def handle(self, *args, **options):

        YES_ANSWER = 'y'

        # Получим объект модели
        try:
            current_obj = apps.get_model(app_label=options['app_name'], model_name=options['model_name'])
        except LookupError:
            print(f"Модель {options['model_name']} в приложении {options['app_name']} не найдена...")
            raise SystemExit(1)

        # print(current_obj.objects.filter(pk=117850))
        answer = input(
            f"Вы действитеольно хотите очистить модель {options['model_name']} в приложении {options['app_name']}? [{YES_ANSWER}/n]: ")
        if answer == YES_ANSWER:
            RebuildDataParseModel.for_model(current_obj)
            print(f"Модель {options['model_name']} была полностью очищена...")

        else:
            print(f"Модель {options['model_name']} не была очищена...")
