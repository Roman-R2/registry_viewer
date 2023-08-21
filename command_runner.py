import logging
import os
import time
from pathlib import Path

import schedule

from mainapp.logger import GetLogger

# Базовая папка для скрипта
BASE_DIR = Path(__file__).resolve().parent

#
COMMAND_RUNNER_LOGGING_LEVEL = logging.DEBUG
# Папка логов
BACKUP_LOG_FOLDER = BASE_DIR / 'logs' / 'command_runner_logs'
# Файл логов
COMMAND_RUNNER_LOG_FILE = BACKUP_LOG_FOLDER / 'command_runner.r2_log'
# Имя логера для создания бэкапов
COMMAND_RUNNER_LOGGER_NAME = 'command_runner_logger'

# Проверка доступности комманд к исполнению в секундах
FREQUENCY_NEW_COMMON_CHECK = 5

# Папка для временного хранения загруженных на обработку файлов
FOLDER_WITH_REGISTRY_FOR_PROCESS = BASE_DIR / 'data' / 'commands_for_launch' / 'files'
# Файл для хранения камманд перед запуском
TXT_FILE_WITH_COMMANDS = BASE_DIR / 'data' / 'commands_for_launch' / 'commands.txt'


class CommandRunnerLogger(GetLogger):
    """ Класс логера для запускальщька команд. """

    # Singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CommandRunnerLogger, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__(
            log_file=COMMAND_RUNNER_LOG_FILE,
            logger_name=COMMAND_RUNNER_LOGGER_NAME,
            log_level=COMMAND_RUNNER_LOGGING_LEVEL
        )


LOGGER = CommandRunnerLogger().get_logger()


def check_command_runner_job():
    with TXT_FILE_WITH_COMMANDS.open(mode='r', encoding='utf-8') as fd:
        commands_from_file = fd.readlines()

    for this_command in commands_from_file:
        for_log = this_command.strip('\n')
        LOGGER.info(f"Обнаружена команда {for_log} запускаем обработку")
        try:
            process = os.system(this_command)
            LOGGER.info(f"Результат выполнения обработки: {process}")
        except Exception as error:
            LOGGER.error(f"Ошибка фыполнения команды: {error}")


        with TXT_FILE_WITH_COMMANDS.open(mode='w', encoding='utf-8') as fd:
            for line in commands_from_file:
                if line != this_command:
                    fd.write(line)


def main():
    message = "RegistryViewer command runner запущен"
    LOGGER.info(message)
    print(message)

    schedule.every(FREQUENCY_NEW_COMMON_CHECK).seconds.do(check_command_runner_job)

    # Стартанем немедленнов первый раз после запуска
    check_command_runner_job()

    while True:
        schedule.run_pending()
        # print(datetime.now(), schedule.jobs)
        time.sleep(1)


if __name__ == "__main__":
    LOGGER.info(" Старт программы ".center(70, '-'))

    # if not pyuac.isUserAdmin():
    #     LOGGER.info("Перезапускаем программу с правами администратора")
    #     pyuac.runAsAdmin()
    # else:
    #     LOGGER.info("Программа запущена с правами администратора")
    main()
