from app.settings_for_db_dump import BACKUP_LOG_FILE, BACKUP_LOGGER_NAME, BACKUP_LOGGING_LEVEL
from app.settings_for_registry_auto_parse import AUTO_PARSE_LOG_FILE, AUTO_PARSE_LOGGER_NAME, AUTO_PARSE_LOGGING_LEVEL
from mainapp.logger import GetLogger


class AutoParseLogger(GetLogger):
    """ Класс логера для автопарсинга. """

    # Singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AutoParseLogger, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__(
            log_file=AUTO_PARSE_LOG_FILE,
            logger_name=AUTO_PARSE_LOGGER_NAME,
            log_level=AUTO_PARSE_LOGGING_LEVEL
        )


class DBDumpLogger(GetLogger):
    """ Класс логера для автопарсинга. """

    # Singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBDumpLogger, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__(
            log_file=BACKUP_LOG_FILE,
            logger_name=BACKUP_LOGGER_NAME,
            log_level=BACKUP_LOGGING_LEVEL
        )