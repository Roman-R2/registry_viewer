"""
Команда, которая запустит процесс создания бэкапа БД
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path

import chardet
from django.conf import settings
from django.core.management import BaseCommand

from mainapp.custom_loggers import DBDumpLogger

LOGGER = DBDumpLogger().get_logger()


class Command(BaseCommand):
    def handle(self, *args, **options):

        PATH_TO_POSTGRES_BIN_FOLDER = Path('C:/Program Files/PostgreSQL/9.6/bin')

        PG_DUMP_EXE_PATH = 'pg_dump.exe'
        DB_NAME = os.getenv("DB_NAME")
        DB_USER = os.getenv("DB_USER")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_PASSWORD = os.getenv("DB_PASSWORD")

        OUTPUT_DUMP_FILE = settings.BASE_DIR.parent / 'data' / 'db_dackups' / f'db_dump_{datetime.now().strftime("%m-%d-%Y-%H-%M-%S")}.sql'

        command_to_execute = f'cd "{str(PATH_TO_POSTGRES_BIN_FOLDER)}" && ' \
                             f'{PG_DUMP_EXE_PATH} ' \
                             f'-U {DB_USER} ' \
                             f'--no-password ' \
                             f'-h {DB_HOST} ' \
                             f'-p {DB_PORT} ' \
                             f'{DB_NAME} ' \
                             f'> {str(OUTPUT_DUMP_FILE)}'

        print(f'{command_to_execute=}')

        try:
            LOGGER.info(f"command_to_execute={command_to_execute}")
            run: subprocess.CompletedProcess = subprocess.run(
                command_to_execute,
                capture_output=True,
                shell=True,
                env={
                    "PGPASSWORD": DB_PASSWORD
                }
            )
            # print(f"{run=}")

            stdout = run.stdout
            stderr = run.stderr

            print(f"{stdout=}")
            print(f"{stderr=}")

            if stdout:
                print(stdout.decode(chardet.detect(stdout)['encoding']))

            if stderr:
                current_error = stderr.decode(chardet.detect(stderr)['encoding'])
                LOGGER.error(current_error)
        except Exception as error:
            LOGGER.error(f"Ошибка выполнения бэкапа БД: {error} {error.args}")
