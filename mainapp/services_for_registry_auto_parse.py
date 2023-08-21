import os
import re
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Union

import schedule
from django.core.management import call_command
from django.utils import timezone

from app import settings_for_registry_auto_parse
from app import settings_for_apps
from app.settings_for_registry_auto_parse import REGISTRY_BACKUP_FOLDER_PATH
from mainapp.custom_loggers import AutoParseLogger
from mainapp.dto import FileStatDTO, RegistryDTO
from statisticapp.models import ParseStatistics
from statisticapp.services import SaveParserError

LOGGER = AutoParseLogger().get_logger()


class DatetimeTransform:

    def __init__(self, native_date: datetime):
        self.native_date = native_date

    def __get_date_with_app_offset_aware(self):
        """ Добавить метку временной зоны проекта в переданный datetime """
        return self.native_date.replace(tzinfo=timezone.localtime().tzinfo)

    @staticmethod
    def get_date_with_app_offset_aware(native_date: datetime):
        return DatetimeTransform(native_date=native_date).__get_date_with_app_offset_aware()


class GetFileStat:
    """ Класс для преобразования Path в GetFileStatDTO """

    def __init__(self, file_path: Path):
        if not file_path.is_file():
            LOGGER.error(f"Переданный путь не является файлом: {file_path}")
            raise ValueError(f"Переданный путь не является файлом: {file_path}")
        self.file_path = file_path

    def __get_file_stat_dto(self) -> FileStatDTO:
        """ Получит необходимую статистику о файле и вернет ее в списке """
        # stat_info.st_atime: Время последнего доступа, выраженное в секундах. (access)
        # stat_info.st_mtime: Время последней модификации контента, выраженное в секундах. (modify)
        # stat_info.st_ctime: Время создания в Windows, выраженное в секундах. (create)
        file_stat = self.file_path.stat()
        return FileStatDTO(
            file_path=self.file_path,
            last_access_time=datetime.fromtimestamp(file_stat.st_atime),
            last_modify_time=datetime.fromtimestamp(file_stat.st_mtime),
            last_create_time=datetime.fromtimestamp(file_stat.st_ctime)
        )

    @staticmethod
    def get_file_stat_dto(file_path: Path):
        return GetFileStat(file_path).__get_file_stat_dto()


class MakeRegistryFileBackup:
    """ Класс для создания бэкапов файлов реестров. """

    def __init__(self, current_file: FileStatDTO, internal_service_registry_name: str):
        self.current_file = current_file
        self.internal_service_registry_name = internal_service_registry_name

    def __start(self):
        """ Создаст бэкап файла. """
        backup_file_name = f"{time.time()}_{self.current_file.file_path.name}"
        try:
            shutil.copy2(
                self.current_file.file_path,
                REGISTRY_BACKUP_FOLDER_PATH / self.internal_service_registry_name / backup_file_name
            )
            LOGGER.info(
                f"Сделали бэкап файла {self.current_file.file_path.name} для реестра {self.internal_service_registry_name}"
            )
        except Exception as error:
            current_error = f'Ошибка создания бэкапа файла {self.current_file.file_path.name} ' \
                            f'для реестра {self.internal_service_registry_name}. ({error})'
            LOGGER.info(current_error)
            SaveParserError.for_registry(
                registry=self.internal_service_registry_name,
                error_message=error,
                addition_data=current_error
            )

    @staticmethod
    def start(current_file: FileStatDTO, internal_service_registry_name: str):
        return MakeRegistryFileBackup(
            current_file=current_file,
            internal_service_registry_name=internal_service_registry_name
        ).__start()


class FolderScanner:
    """ Предназначен для сканирования папок из преданного списка на предмет новых данных в этих папках."""

    def __init__(self):
        self.registry_settings = settings_for_apps.REGISTRY_DATA

    # self.app_settings: SettingsDTO = app_settings
    # Все найденные при сканировании файлы, которые подходят для вынесения решения на отправку в парсинг
    # self.finding_files: List[FileStatDTO] = []

    def __get_true_file_format(self, file_format_tuple: Tuple[str, ...]) -> Tuple[str, ...]:
        """ Если формат файла не содержит точку в начале, то дополнит точкой и вернет отформатированный кортеж.
         Также если формат установит в нижний регистр."""
        return tuple(
            file_format.lower() if file_format[0] == '.' else '.' + file_format.lower()
            for file_format in file_format_tuple
        )

    def file_format_to_lowercase(self, filename_list: List[str]) -> List[str]:
        """ Вернет список с именами файлов с форматом в нижнем регистре."""
        new_list = []
        for filename in filename_list:
            split_filename = filename.split('.')
            split_filename[-1] = split_filename[-1].lower()
            new_list.append('.'.join(split_filename))
        return new_list

    def get_patterned_files(self, filename_list: List[str], regular_expression: re) -> List[str]:
        """ Предназначен для получения списка файлов исходя из данных по путям и шаблонам названия файла. """
        return [item for item in filename_list if re.fullmatch(regular_expression, os.path.splitext(item)[0])]

    def scan_folders_job(self):
        """ Просканирует все директории из настроек и получит все файлы, которые не директории
        и формат у которых сходится с шаблоном. """

        # Получим данные для автоматического сканирования папок из настроек
        # data_for_auto_scan: List[UnitForScanDTO] = [item.data_for_auto_scan for item in self.registry_settings]
        # data_for_auto_scan: List[UnitForScanDTO] = [item.data_for_auto_scan for item in self.registry_settings][0]
        print('Итерации сканирования папок регистров'.center(79, '-'))

        for registry_item in self.registry_settings:
            # Проверим, что настройки заданы, если нет - пропускаем
            if (
                    isinstance(registry_item.data_for_auto_scan.folder_path, (Path, type(None)))
                    and registry_item.data_for_auto_scan.folder_path is None
            ):
                continue
            # Проверим, что папка для сканирования вообще существует
            if not registry_item.data_for_auto_scan.folder_path.exists():
                LOGGER.error(
                    f"Папка {registry_item.data_for_auto_scan.folder_path} не существует на данном компьютере.")
            else:
                prepared_finding_files = []
                finding_files_part = [
                    registry_item.data_for_auto_scan.folder_path / filename
                    for filename in self.get_patterned_files(
                        self.file_format_to_lowercase(os.listdir(registry_item.data_for_auto_scan.folder_path)),
                        registry_item.data_for_auto_scan.reqexp_pattern
                    )
                    if not os.path.isdir(
                        os.path.join(registry_item.data_for_auto_scan.folder_path, filename)) and filename.endswith(
                        self.__get_true_file_format(registry_item.data_for_auto_scan.allowed_file_formats)
                    )
                ]
                prepared_finding_files += [
                    GetFileStat.get_file_stat_dto(item)
                    for item in finding_files_part
                ]
                # print(f"{registry_item.internal_service_registry_name}: {prepared_finding_files}")
                LOGGER.info(f"Для {registry_item.internal_service_registry_name} по "
                            f"шаблону подходят файлы {prepared_finding_files}."
                            f"Отправляем найденные файлы на вынесение решения о парсинге по ним."
                            )

                # Отправляем найденные файлы на вынесение решения о парсинге по ним
                MakeDecisionForFiles(
                    files_for_decision=prepared_finding_files,
                    current_registry_settings=registry_item
                ).launch()


class MakeDecisionForFiles:
    """ Педназначен для вынесения решения по списку переданных файлов,
    нужно ли отправлять их на обработку как новые файлы или нет. """

    def __init__(self, files_for_decision: List[FileStatDTO], current_registry_settings: RegistryDTO):
        # список файлов из сканируемой папки, которые прошли по условиям
        self.files_for_decision = files_for_decision
        # Настройки текущего реестра
        self.current_registry_settings: RegistryDTO = current_registry_settings

    def __is_necessary_to_parse(self, file: FileStatDTO) -> bool:
        """ Определит необходимость для отправки данных файла на парсеры и вернет bool. """
        # Получим для указанного регистра последнюю статистику по парсингу, которая полностью окончена
        last_parser_activity = ParseStatistics.objects.filter(
            registry_name=self.current_registry_settings.internal_service_registry_name
        ).order_by('-parse_end_date').first()
        # Если в таблице ничего пока нет
        if last_parser_activity is None:
            return True
        # Если у нового файла время модификации свежее, чем у уже спарсеного из базы
        if (
                last_parser_activity.file.last_modify_time.astimezone(timezone.localtime().tzinfo) <
                DatetimeTransform.get_date_with_app_offset_aware(file.last_modify_time)
        ):
            LOGGER.info(
                f"Файл {file.file_path.name} для реестра "
                f"{self.current_registry_settings.internal_service_registry_name} "
                f"вынесено решение о необходимости загрузки данных"
            )
            print(
                f"Файл '{file.file_path.name}' для реестра "
                f"{self.current_registry_settings.internal_service_registry_name} "
                f"вынесено решение о необходимости загрузки данных"
            )
            return True
        LOGGER.info(
            f"Файл {file.file_path.name} для реестра "
            f"{self.current_registry_settings.internal_service_registry_name} "
            f"не нуждается в обработке (файл уже был обработан)."
        )
        print(
            f"Файл {file.file_path.name} для реестра "
            f"{self.current_registry_settings.internal_service_registry_name} "
            f"не нуждается в обработке (файл уже был обработан)."
        )
        return False

    def __take_the_most_recent_file_for_last_modify_time(self) -> Union[FileStatDTO, None]:
        """ Возмет самый свежий файл из переданного списка файлов по атрибуту last_modify_time. """
        most_recent_file = None
        for item_file in self.files_for_decision:
            if most_recent_file is None:
                most_recent_file = item_file
            else:
                if item_file.last_modify_time > most_recent_file.last_modify_time:
                    most_recent_file = item_file
        return most_recent_file

    def launch(self):
        # Возьмем самай свежий файл
        most_recent_file = self.__take_the_most_recent_file_for_last_modify_time()
        # И если он существует, то проверим на необходимость парсинга
        if most_recent_file is not None:
            if self.__is_necessary_to_parse(most_recent_file):
                SendFileToParse(
                    file_for_parse=most_recent_file,
                    current_registry_settings=self.current_registry_settings
                ).process()


class SendFileToParse:
    """ Отвечает за отправку файла на парсинг. """

    # thread_pool_executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS_FOR_THREAD_POOL_EXECUTOR)

    def __init__(self, file_for_parse: FileStatDTO, current_registry_settings: RegistryDTO):
        # Файл, который необходимо обработать
        self.file_for_parse: FileStatDTO = file_for_parse
        # Настройки текущего реестра
        self.current_registry_settings: RegistryDTO = current_registry_settings

    def process(self):
        """ Запустит процесс парсинга фалов. """
        if self.file_for_parse.file_path.exists():
            call_command(
                self.current_registry_settings.data_for_auto_scan.command_name_for_cli_parse,
                [
                    self.current_registry_settings.internal_service_registry_name  # метка реестра
                    , self.file_for_parse.file_path
                ],
                # auto_parse=True
            )
        else:
            LOGGER.error(f"Выбранный в классе {__class__} файл {self.file_for_parse.file_path} не существует.")


class CheckRegistryForFreshDataForParseDecision:
    """ Предназначен запуска непрерывного процесса проверки регистров
    на свежесть данных для вынесения решения по их добавлению в БД."""

    def registry_check_for_fresh_data_job(self):
        """ Запускает работу по проверке регистров на свежесть данных для вынесения решения по их добавлению в БД. """
        LOGGER.info(
            'Запускаем работу по проверке регистров на свежесть данных для вынесения решения по их добавлению в БД.'
        )
        FolderScanner().scan_folders_job()

    def launch(self) -> None:
        schedule.every(settings_for_registry_auto_parse.REGISTRY_CHECKING_MINUTES_FREQUENCY).minutes.do(
            self.registry_check_for_fresh_data_job)

        # Стартанем немедленнов первый раз после запуска
        self.registry_check_for_fresh_data_job()

        while True:
            schedule.run_pending()
            # print(datetime.now(), schedule.jobs)
            time.sleep(10)


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
