import sys
import traceback
from pathlib import Path
from typing import List

from django.core.management import BaseCommand
from django.utils.timezone import localtime

from mainapp.custom_loggers import AutoParseLogger
from mainapp.services import RebuildDataParseModel, WorkWithXLSXFiles
from mainapp.services_for_registry_auto_parse import GetFileStat, DatetimeTransform, MakeRegistryFileBackup
from registry_lrp.dto import RegistryLRPDopDTO
from statisticapp.models import ParseFileStat
from statisticapp.services import WorkWithStatistic, SaveParserError, SaveParseStatistic

LOGGER = AutoParseLogger().get_logger()


class Command(BaseCommand):
    help = 'Команда для парсинга реестра безработных.'

    CURRENT_DTO = RegistryLRPDopDTO
    EXCLUDE_COUNT_OF_LINES_FROM_FILE = 2

    def add_arguments(self, parser):
        # Аргумент показывает необходимость в автопарсинге, если его нет, то парсинг будет в ручном режиме
        # parser.add_argument(
        #     '-ap',
        #     '--auto_parse',
        #     action='store_true',
        #     default=False,
        #     help='Метка автопарсинга реестра'
        # )

        parser.add_argument(
            '-fp',
            '--full_parse',
            action='store_true',
            default=True,
            help='Метка о необходимости полной загрузки'
        )

        parser.add_argument(
            nargs='*',
            type=str,
            help='Дополнительные параметры для команды',
            dest='args'
        )

    def handle(self, *args, **options):
        self.__process_parsing(*args, **options)

    def __process_parsing(self, *args, **options):
        """ Обработает процедуру парсинга регистров """
        PARSE_START_DATE = localtime()

        try:
            folder_for_processing: Path = Path(args[0])
        except IndexError:
            raise ValueError(f"Вы не ввели папку с файлами ЛИРП")

        internal_service_registry_name = 'registry_lrp_dop'

        LOGGER.info(f"Обрабатываем реестр {internal_service_registry_name}.")

        # Поменяем таблицу для записи
        current_model = WorkWithStatistic.get_next_model_obj(internal_service_registry_name)

        if options['full_parse']:
            # Пересоздадим таблицу в БД для модели, которую будем сейчас использовать
            RebuildDataParseModel.for_model(current_model)
            LOGGER.info(f"Полностью очистили данные в модели {current_model.__class__}.")

        if folder_for_processing.is_dir():
            files_in_folder: List[Path] = [
                filepath
                for filepath in folder_for_processing.iterdir()
                if filepath.suffix == ".xlsx" and filepath.name[0] != "~"
            ]
        else:
            current_error = f"Путь {folder_for_processing.resolve()} не является папкой"
            LOGGER.error(current_error)
            raise ValueError(current_error)

        counter_dto_parse_errors = 0
        counter_orm_parse_errors = 0

        all_row_counter = 0

        for filepath in files_in_folder:
            LOGGER.info(f"Используем файл реестра {filepath.resolve()}...")
            print(f"Используем файл реестра {filepath.resolve()}...")

            row_counter = 0

            file_for_processing_dto = GetFileStat.get_file_stat_dto(Path(filepath))
            line_cache = []
            for line in tuple(WorkWithXLSXFiles.get_lxsx_file_line_iterator(filepath)):
                # Если строку сначала файла не нужно обрабатывать - то пропускаем
                if row_counter < self.EXCLUDE_COUNT_OF_LINES_FROM_FILE:
                    row_counter += 1
                    continue

                #     # Поместим данные строки в ДТО
                try:
                    # Если это строка - где второй номер телефона, то просто пропустим его
                    if any([bool(str(item).strip()) for item in line]) is False:
                        continue

                    # print(line)
                    # Если начало строки пустое, то возьмем из предидущей строки
                    if any([bool(str(item).strip()) for item in line[:9]]) is False:
                        line = line_cache + line[9:]
                    else:
                        line_cache = line

                    row_dto = self.CURRENT_DTO(
                        adult_fio=line[1],
                        adult_passport_data=line[2],
                        adult_registration_address=line[3],
                        # Орган, выдавший документ
                        issuing_authority=line[4],
                        # Дата решения
                        decision_date=line[5],
                        # Номер и дата дела
                        case_number_and_date=line[6],
                        # Дата вступления решения в законную силу
                        decision_entry_into_force_date=line[7],
                        # Результат рассмотрения
                        review_result=line[8],
                        child_fio=line[9],
                        child_birthday=line[10],
                        # Наименование документа-основания
                        name_foundation_document=line[11],
                        # Реквизиты документа-основания
                        details_foundation_document=line[12],
                    )

                except Exception as error:
                    print(' Ошибка добавления в DTO '.center(69, '-'))
                    print(line)
                    error_type, error_value, error_trace = sys.exc_info()
                    print("Type: ", error_type)
                    print("Value:", error_value)
                    print("Trace:", error_trace)
                    traceback.print_exception(error_type, error_value, error_trace, limit=5, file=sys.stdout)
                    print('-'.center(69, '-'))
                    current_error = f'Ошибка добавления в DTO: {self.CURRENT_DTO.__name__}. split_line: {line}.'
                    LOGGER.error(current_error)
                    SaveParserError.for_registry(
                        registry=internal_service_registry_name,
                        error_message=error,
                        addition_data=current_error
                    )
                    continue

                # Сохраним данные строки в таблицу
                try:
                    current_model.objects.create(
                        **row_dto.get_data
                    )
                except Exception as error:
                    print(' Ошибка добавления в DTO '.center(69, '-'))
                    error_type, error_value, error_trace = sys.exc_info()
                    print("Type: ", error_type)
                    print("Value:", error_value)
                    print("Trace:", error_trace)
                    traceback.print_exception(error_type, error_value, error_trace, limit=5, file=sys.stdout)
                    print('-'.center(69, '-'))

                    current_error = f'Ошибка ORM. len(split_line): {len(line)}. split_line: {line}. **row_dto.get_data: {dict(**row_dto.get_data)}'
                    # LOGGER.error(current_error)
                    SaveParserError.for_registry(
                        registry=internal_service_registry_name,
                        error_message=error,
                        addition_data=current_error
                    )
                    continue

                row_counter += 1
                all_row_counter += 1

            LOGGER.info(
                f"Обработка реестра {internal_service_registry_name} окончена. "
                f"Всего строк обработано: {all_row_counter} шт. Ошибок добавления в DTO: {counter_dto_parse_errors} шт. "
                f"Ошибок ORM: {counter_orm_parse_errors} шт."
            )

            # Сохраним данные статистики о произошелшем процессе парсинга в соотетствующую таблицу
            file_for_processing_dto_obj = ParseFileStat.objects.create(
                file_path=file_for_processing_dto.file_path,
                last_access_time=DatetimeTransform.get_date_with_app_offset_aware(
                    file_for_processing_dto.last_access_time),
                last_modify_time=DatetimeTransform.get_date_with_app_offset_aware(
                    file_for_processing_dto.last_modify_time),
                last_create_time=DatetimeTransform.get_date_with_app_offset_aware(
                    file_for_processing_dto.last_create_time)
            )

            # print(f"{file_for_processing_dto=}")

            # Сделаем бэкап файла
            MakeRegistryFileBackup.start(
                current_file=file_for_processing_dto,
                internal_service_registry_name=internal_service_registry_name
            )

        save_parse_statistic_obj = SaveParseStatistic.for_registry(
            file=file_for_processing_dto_obj,
            registry=internal_service_registry_name,
            parse_start_date=PARSE_START_DATE,
            parse_end_date=localtime(),
            parse_model_name=current_model.__name__,
            parse_number_of_lines=all_row_counter
        )
        LOGGER.info(
            f"Сохранили данные статистики об окончании парсинга {file_for_processing_dto}. "
            f"{SaveParseStatistic.__name__}: id {save_parse_statistic_obj.id}"
        )
