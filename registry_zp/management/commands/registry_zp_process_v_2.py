import sys
import traceback
from pathlib import Path
from zipfile import BadZipFile

from django.core.management import BaseCommand
from django.utils.timezone import localtime
from tqdm import tqdm

from app.settings_for_registry_auto_parse import TEMP_FILE_EXTRACTION_DIR
from mainapp.custom_loggers import AutoParseLogger
from mainapp.dto import RegistryDataForCommandDTO
from mainapp.services import RebuildDataParseModel, ProcessZipFileV2, PreprocessingRawStringV2
from mainapp.services_for_registry_auto_parse import GetFileStat, DatetimeTransform, MakeRegistryFileBackup
from registry_lrp.dto import RegistryZpDTO
from statisticapp.models import ParseFileStat
from statisticapp.services import WorkWithStatistic, SaveParserError, SaveParseStatistic

LOGGER = AutoParseLogger().get_logger()


class Command(BaseCommand):
    help = 'Команда для парсинга реестра законных представителей.'

    CURRENT_DTO = RegistryZpDTO

    def add_arguments(self, parser):

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

    def _except_error_in_log_and_console(self, current_error: str) -> None:
        """ Выведет ошибку в консоль и запишет ее в логи. """
        print('-'.center(69, '-'))
        LOGGER.error(current_error)
        error_type, error_value, error_trace = sys.exc_info()
        print("Type: ", error_type)
        print("Value:", error_value)
        print("Trace:", error_trace)
        traceback.print_exception(error_type, error_value, error_trace, limit=5, file=sys.stdout)
        print('-'.center(69, '-'))

    def __process_parsing(self, *args, **options):
        """ Обработает автоматическую процедуру парсинга регистров """

        PARSE_START_DATE = localtime()

        registry_settings = RegistryDataForCommandDTO(
            internal_service_registry_name=args[0],
            file_for_processing=args[1]
        )

        file_for_processing_dto = GetFileStat.get_file_stat_dto(Path(registry_settings.file_for_processing))

        LOGGER.info(f"Обрабатываем реестр {registry_settings.internal_service_registry_name} в автоматическом режиме.")

        # Поменяем таблицу для записи
        current_model = WorkWithStatistic.get_next_model_obj(registry_settings.internal_service_registry_name)

        if options['full_parse']:
            # Пересоздадим таблицу в БД для модели, которую будем сейчас использовать
            RebuildDataParseModel.for_model(current_model)
            LOGGER.info(f"Полностью очистили данные в модели {current_model.__class__}.")

        process_zip_file_obj = ProcessZipFileV2(
            registry_settings.file_for_processing,
            TEMP_FILE_EXTRACTION_DIR
        )

        try:
            extract_file_name = process_zip_file_obj.extract_file_from_zip
        except BadZipFile as error:
            current_error = f"Плохой zip-файл {registry_settings.file_for_processing}..."
            self._except_error_in_log_and_console(current_error)
        except Exception as error:
            LOGGER.error(self._except_error_in_log_and_console(f'Не отловленная ошибка...'))
        else:

            LOGGER.info(f"Распаковали файл реестра {extract_file_name}...")

            counter_dto_parse_errors = 0
            counter_orm_parse_errors = 0

            with open(TEMP_FILE_EXTRACTION_DIR / extract_file_name, mode='r') as csv_file:
                row_counter = 0
                for line in tqdm(tuple(csv_file)):

                    # Если заголовок, то пропускаем
                    if row_counter == 0:
                        row_counter += 1
                        continue

                    processed_line = PreprocessingRawStringV2.process(line)

                    split_line = processed_line.split(';')

                    # Поместим данные строки в ДТО
                    try:
                        prepared_dict = {
                            'adult_snils': split_line[0].strip().replace('"', ''),
                            'child_snils': split_line[1].strip().replace('"', ''),
                            'adult_fio': split_line[2].strip().replace('"', ''),
                            'child_fio': split_line[3].strip().replace('"', ''),
                            'event_type_code': split_line[5].strip().replace('"', ''),
                            'effective_date': split_line[6].strip(),
                            'series_of_document': split_line[7].strip().replace('"', ''),
                            'document_number': split_line[8].strip(),
                            'issuing_authority': split_line[9].strip(),
                            'document_date': split_line[10].strip(),
                        }
                    except IndexError:
                        current_error = f'Произошла ошибка парсинга: line: {line} processed_line: {processed_line} split_line: {split_line}'
                        LOGGER.error(current_error)
                        break

                    try:
                        row_dto = self.CURRENT_DTO(
                            **prepared_dict
                        )
                    except Exception as error:
                        current_error = (
                            f'Ошибка добавления в DTO: {self.CURRENT_DTO.__name__}. '
                            f'split_line: {split_line}. '
                            f'len(prepared_dict): {len(prepared_dict)}, prepared_dict: {prepared_dict}')
                        # print('--->', current_error)
                        self._except_error_in_log_and_console(current_error=current_error)
                        # LOGGER.error(current_error)
                        SaveParserError.for_registry(
                            registry=registry_settings.internal_service_registry_name,
                            error_message=error,
                            addition_data=current_error
                        )
                        counter_dto_parse_errors += 1
                        continue

                    # Сохраним данные строки в таблицу
                    try:
                        current_model.objects.create(
                            **row_dto.get_data
                        )
                    except Exception as error:
                        current_error = f'Ошибка ORM. ' \
                                        f'line: {line}' \
                                        f'len(split_line): {len(split_line)}.' \
                                        f'split_line: {split_line}.' \
                                        f'len(**row_dto.get_data): {len(dict(**row_dto.get_data))}' \
                                        f'**row_dto.get_data: {dict(**row_dto.get_data)}'
                        self._except_error_in_log_and_console(current_error=current_error)
                        SaveParserError.for_registry(
                            registry=registry_settings.internal_service_registry_name,
                            error_message=error,
                            addition_data=current_error
                        )
                        counter_orm_parse_errors += 1
                        continue

                    row_counter += 1

            LOGGER.info(
                f"Обработка реестра {registry_settings.internal_service_registry_name} окончена. "
                f"Всего строк обработано: {row_counter - 1} шт. Ошибок добавления в DTO: {counter_dto_parse_errors} шт. "
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

            save_parse_statistic_obj = SaveParseStatistic.for_registry(
                file=file_for_processing_dto_obj,
                registry=registry_settings.internal_service_registry_name,
                parse_start_date=PARSE_START_DATE,
                parse_end_date=localtime(),
                parse_model_name=current_model.__name__,
                parse_number_of_lines=row_counter - 1
            )
            LOGGER.info(
                f"Сохранили данные статистики об окончании парсинга {file_for_processing_dto.file_path.name}. "
                f"{SaveParseStatistic.__name__}: id {save_parse_statistic_obj.id}"
            )

            # Сделаем бэкап файла
            MakeRegistryFileBackup.start(
                current_file=file_for_processing_dto,
                internal_service_registry_name=registry_settings.internal_service_registry_name
            )
