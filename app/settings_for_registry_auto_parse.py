import logging

from django.conf import settings

from mainapp.dto import ParseCompareSettings

# --------------  Настройки логирования
# Уровень логирования
AUTO_PARSE_LOGGING_LEVEL = logging.DEBUG
# Папка логов
AUTO_PARSE_LOG_FOLDER = settings.BASE_DIR / 'logs' / 'registry_auto_parse_logs'
# Файл логов
AUTO_PARSE_LOG_FILE = AUTO_PARSE_LOG_FOLDER / 'registry_auto_parse.r2_log'
# Имя логера для автопарсинга регистров
AUTO_PARSE_LOGGER_NAME = 'registry_auto_parse_logger'

# Частота (в минутах) процесса запуска проверки регистров на свежесть данных, для вынесения решения по сбору данных в БД
REGISTRY_CHECKING_MINUTES_FREQUENCY = 60  # минут
# Путь до папки с бэкапами регистров, которые образуются после успешного процесса парсинга
REGISTRY_BACKUP_FOLDER_PATH = settings.BASE_DIR / 'data' / 'backup_folder'
# Папка для временной распаковки (при необходимости) zip архивов реестров
TEMP_FILE_EXTRACTION_DIR = settings.BASE_DIR / 'data' / 'extracted_files'

# Метрики для сопоставления данных парсинга и ожидаемых
RTN_TS_REGISTRY_PARSE_COMPARE = ParseCompareSettings(
    # Ожидаемая длина строки (колличество заполненых данными ячеек в строке)
    row_len=4,
    # Количество строк, которые нужно пропустить до появления полезной инофрмации
    exclude_line_count=4,
    # Порядок столбцов данных в файле
    file_columns=['Наименование', 'Год вып.', 'Владелец', 'Дата рождения']
)
