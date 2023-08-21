import logging

from django.conf import settings

# --------------  Настройки логирования
# Уровень логирования
BACKUP_LOGGING_LEVEL = logging.DEBUG
# Папка логов
BACKUP_LOG_FOLDER = settings.BASE_DIR / 'logs' / 'bd_backup_logs'
# Файл логов
BACKUP_LOG_FILE = BACKUP_LOG_FOLDER / 'db_dump.r2_log'
# Имя логера для создания бэкапов
BACKUP_LOGGER_NAME = 'db_dump_logger'

# -----------------
DB_DUMP_FOLDER = settings.BASE_DIR / 'data' / 'db_dackups'