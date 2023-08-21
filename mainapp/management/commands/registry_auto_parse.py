"""
Команда  запуска процесса автоматического парсинга данных
"""
from datetime import datetime

import psutil
from django.core.management import BaseCommand
from django.utils import timezone

from app.settings_for_registry_auto_parse import REGISTRY_CHECKING_MINUTES_FREQUENCY
from mainapp.custom_loggers import AutoParseLogger
from mainapp.services_for_registry_auto_parse import CheckRegistryForFreshDataForParseDecision, FolderScanner
from statisticapp.models import ParseProcess

LOGGER = AutoParseLogger().get_logger()


class Command(BaseCommand):
    def handle(self, *args, **options):
        process_obj = psutil.Process()
        process_obj_dict = process_obj.as_dict()

        main_message = (
            f"Запустили автоматическую обработку регистров с периодичностью "
            f"в {REGISTRY_CHECKING_MINUTES_FREQUENCY} минут."
        )
        LOGGER.info(main_message)
        print(main_message)

        # Добавим данные в таблице о запущенных процессах автоматического парсинга
        ParseProcess.objects.create(
            pid=process_obj_dict['pid'],
            name=process_obj_dict['name'],
            started_at=datetime.fromtimestamp(
                process_obj_dict['create_time'],
                tz=timezone.localtime().tzinfo
            )
        )
        LOGGER.info(
            f"Записали в БД через модель {ParseProcess.__name__} данные о запущеном процессе "
            f"(pid: {process_obj_dict['pid']}, process name: {process_obj_dict['name']})"
        )

        # Запустим непрерыный процесс проверки регистров на свежесть данных для вынесения решения по их добавлению в БД
        CheckRegistryForFreshDataForParseDecision().launch()

        # FolderScanner().scan_folders_job()
