import sys
import traceback
from pathlib import Path

from django.core.management import BaseCommand
from django.utils.timezone import localtime
from tqdm import tqdm

from app.settings_for_registry_auto_parse import RTN_TS_REGISTRY_PARSE_COMPARE
from mainapp.custom_loggers import AutoParseLogger
from mainapp.dto import RegistryDataForCommandDTO
from mainapp.services import RebuildDataParseModel, PreprocessingRawStringV2, WorkWithXLSXFiles, ProcessZipFileV2
from mainapp.services_for_registry_auto_parse import GetFileStat, DatetimeTransform, MakeRegistryFileBackup
from registry_lrp.dto import RegistryRtnTsDTO
from statisticapp.models import ParseFileStat
from statisticapp.services import WorkWithStatistic, SaveParserError, SaveParseStatistic

LOGGER = AutoParseLogger().get_logger()


class Command(BaseCommand):
    help = 'Команда для парсинга реестра безработных.'

    CURRENT_DTO = RegistryRtnTsDTO
    EXCLUDE_COUNT_OF_LINES_FROM_FILE = RTN_TS_REGISTRY_PARSE_COMPARE.exclude_line_count

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

        logic_parse_error = False

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
            LOGGER.info(f"Полностью очистили данные в модели {current_model.__name__}.")

        counter_dto_parse_errors = 0
        counter_orm_parse_errors = 0

        row_counter = 0

        lxsx_line_iterator = None
        try:
            lxsx_line_iterator = tuple(WorkWithXLSXFiles.get_lxsx_file_line_iterator(file_for_processing_dto.file_path))
        except KeyError as error:
            logic_parse_error = True
            LOGGER.error(f"Скорее всего XLSX-файл для {Path(__file__).resolve().stem} не корректен. Ошибка: {error}")

        if logic_parse_error:
            LOGGER.error(f"Парсинг для {Path(__file__).resolve().stem} не произведен.")
        else:
            check_row_len = False
            for line in tqdm(lxsx_line_iterator):
                # Если строку сначала файла не нужно обрабатывать - то пропускаем
                if row_counter < self.EXCLUDE_COUNT_OF_LINES_FROM_FILE:
                    row_counter += 1
                    continue

                if not check_row_len and len(line) != RTN_TS_REGISTRY_PARSE_COMPARE.row_len:
                    LOGGER.error(
                        f"Не соответствует количество ячеек данных строки в файле "
                        f"{registry_settings.file_for_processing}. "
                        f"Ожидается {RTN_TS_REGISTRY_PARSE_COMPARE.row_len}. Получено {len(line)}. "
                        f"Ожидаемый порядок столбцов в файле: {RTN_TS_REGISTRY_PARSE_COMPARE.file_columns}"
                    )
                    logic_parse_error = True
                    break
                else:
                    check_row_len = True

                # Поместим данные строки в ДТО
                try:
                    # Если это строка - где второй номер телефона, то просто пропустим его
                    if line[1] == '' and line[2] == '' and line[3] == '':
                        continue
                    row_dto = self.CURRENT_DTO(
                        fio=line[2],
                        date_of_birth=line[3],
                        ts_name=line[0],
                        ts_year_of_construct=line[1],

                    )
                except Exception as error:
                    current_error = f'Ошибка добавления в DTO: {self.CURRENT_DTO.__name__}. split_line: {line}.'
                    self._except_error_in_log_and_console(current_error)

                    SaveParserError.for_registry(
                        registry=registry_settings.internal_service_registry_name,
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
                    current_error = f'Ошибка ORM. len(split_line): {len(line)}. split_line: {line}. **row_dto.get_data: {dict(**row_dto.get_data)}'
                    self._except_error_in_log_and_console(current_error)
                    SaveParserError.for_registry(
                        registry=registry_settings.internal_service_registry_name,
                        error_message=error,
                        addition_data=current_error
                    )
                    continue

                row_counter += 1

            if not logic_parse_error:
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
