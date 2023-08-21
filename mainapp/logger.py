import logging
import logging.handlers
import sys
from pathlib import Path


class GetLogger:
    """ Служит для определения и инициализации логгера северной стороны. """

    logger_format = '%(asctime)s %(levelname)s %(filename)s : %(message)s'

    # # Singleton
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, 'instance'):
    #         cls.instance = super(GetLogger, cls).__new__(cls)
    #     return cls.instance

    def __init__(
            self,
            log_file: Path,
            log_encoding: str = 'utf-8',
            log_level: int = logging.DEBUG,
            logger_name: str = 'canvas_logger',

    ):
        # Создаём формировщик логов (formatter):
        self.log_file = log_file
        self.log_level = log_level
        self.log_encoding = log_encoding
        self.server_formatter = logging.Formatter(self.logger_format)
        # Подготовка имени файла для логирования
        self.logger = logging.getLogger(logger_name)
        self._add_handlers()
        self.logger.setLevel(self.log_level)

    def _get_stderr_handler(self):
        """ Создаст поток вывода логов в поток вывода ошибок. """
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(self.server_formatter)
        stream_handler.setLevel(logging.ERROR)
        return stream_handler

    def _get_rotating_file_handler(
            self,
            interval_value: int = 1,
            interval_period: str = 'D'
    ):
        """
        Регистрация логирования в виде отдельных файлов, которые
        создаются с указанным интервалом.
        :param interval_value: Числовое значение для интервала
        :param interval_period: Период интервала, через который создается файл
        :return:
        """
        log_file = logging.handlers.TimedRotatingFileHandler(
            self.log_file,
            encoding=self.log_encoding,
            interval=interval_value,
            when=interval_period
        )
        log_file.setFormatter(self.server_formatter)
        return log_file

    def _get_simple_file_handler(self):
        """ Регистрация логирования в виде простого файла. """
        log_file = logging.FileHandler(
            self.log_file,
            encoding=self.log_encoding
        )
        log_file.setFormatter(self.server_formatter)
        return log_file

    def _add_handlers(self):
        """ Создаём и настраиваем регистраторы. """
        if not self.logger.hasHandlers():
            self.logger.addHandler(self._get_stderr_handler())
            self.logger.addHandler(self._get_rotating_file_handler())

    def get_logger(self):
        return self.logger


if __name__ == '__main__':
    print(f"Данный файл {__file__} следует подключить к проекту как модуль.")
