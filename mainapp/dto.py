from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Tuple, List, Union


class ParseCompareSettings(NamedTuple):
    # Ожидаемая длина строки (колличество заполненых данными ячеек в строке)
    row_len: int
    # Количество строк, которые нужно пропустить до появления полезной инофрмации
    exclude_line_count: int
    # Порядок столбцов данных в файле
    file_columns: List


class UnitForScanDTO(NamedTuple):
    """ DTO содержит информацию необходимую для сканирования папок на предмет новых файлов для парсинга данных."""
    # Путь до папки, в которой находятся файлы для сканирования
    folder_path: Union[Path, None]
    # Шаблон для регулярного выражения я прямого сопоставления с именен файла
    reqexp_pattern: Union[str, None]
    # Кортеж, содержащий форматы файлов для сканирования в виде строки (регистр, верхний или нижний, не важен)
    allowed_file_formats: Union[Tuple[str, ...], None]
    # Команда, для запуска процесса парсинга файла регистра (django command name)
    command_name_for_cli_parse: Union[str, None]
    # Путь к папке для бэкапов регистра
    path_to_backup_folder: Path


class CommonSearchDTO(NamedTuple):
    # список имен полей согласно модели таблицы регистра для поиска по СНИЛС
    search_list_for_snils: List[str]


class RegistryDTO(NamedTuple):
    """ DTO содержит информацию о регистре. """
    # (короткое имя, длинное имя, внутренние название приложения, массив названий полей для поиска по СНИЛС)
    # короткое имя регистра
    short_registry_name: str
    # длинное имя регистра
    long_registry_name: str
    # название регистра для внутреннего использования приложением
    internal_service_registry_name: str
    # списки полей для общего поиска по ним данных
    fields_for_common_search: CommonSearchDTO
    # Разрешенные модели для сохранения фанных в БД
    allowed_models: Tuple
    # данные для автоматического сканирования и заполнения регистров
    data_for_auto_scan: UnitForScanDTO


class FileStatDTO(NamedTuple):
    # Полный путь до файла
    file_path: Path
    # Время последнего доступа. (access)
    last_access_time: datetime
    # Время последней модификации контента. (modify)
    last_modify_time: datetime
    # Время создания. (create)
    last_create_time: datetime


class RegistryDataForCommandDTO(NamedTuple):
    # Метка регистра для внутреннего пользования
    internal_service_registry_name: str
    # Путь до файла, который нужно обработать
    file_for_processing: Path


class LinkMenuDTO(NamedTuple):
    """ DTO для предачи данных о регистрах в отображение их на странице и в ссылках. """
    # Короткое имя регистра
    registry_short_name: str
    # Развернутое имя регистра
    registry_description: str
    # Время последнего парсинга регистра
    registry_last_parse_date: datetime
    # Название регистра для внутреннего использования приложением
    internal_service_registry_name: str
