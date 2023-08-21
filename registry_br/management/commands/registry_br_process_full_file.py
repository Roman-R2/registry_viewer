import shutil
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand
import os

from django.utils import timezone
from tabulate import tabulate

from tqdm import tqdm

from registry_lrp.dto import RegistryBrDTO
from mainapp.services import File, RebuildDataParseModel, WorkWithXLSXFiles, center_print
from statisticapp.services import SaveParserError, SaveParseStatistic, WorkWithStatistic


class Command(BaseCommand):
    def handle(self, *args, **options):
        CURRENT_DTO = RegistryBrDTO
        # REGISTRY_CHOICE_MARK = RegistryNameChoices.REGISTRY_BR
        APP_NAME = 'registry_br'
        FILE_FOLDER = Path(r'C:\Users\027SlyusarRV\Documents\Реестры')
        APP_BACKUP_FOLDER = os.path.join(settings.BACKUP_FOLDER, APP_NAME)
        # Сколько строк с начала файла не обрабатывать
        EXCLUDE_COUNT_OF_LINES_FROM_FILE = 2
        PARSE_START_DATE = timezone.now()
        # Показывать ли traceback ошибки при добавлениив DTO
        VERBOSE = True

        files = os.listdir(FILE_FOLDER)

        center_print(' Добавление данных из файла в текущую теблицу БД для реестра БР ')

        print("Выберите файл для обработки:")
        table = []
        for choice, file in enumerate(files):
            table.append(
                [
                    f'{choice + 1}.',
                    file,
                    datetime.utcfromtimestamp(
                        os.stat(os.path.join(FILE_FOLDER, file)).st_ctime
                    ).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.utcfromtimestamp(
                        os.stat(os.path.join(FILE_FOLDER, file)).st_mtime
                    ).strftime('%Y-%m-%d %H:%M:%S')
                ]
            )

        print(tabulate(table, headers=['Выбор', 'Имя файла', 'Создан', 'Изменен']))

        while True:
            try:
                user_choice = int(input("Выбор: "))
                user_file = files[user_choice - 1]
                break
            except ValueError:
                print('--> Введите номер файла (целое число)')
            except IndexError:
                print('--> Такого номера файла нет в возможностях выбора.')

        center_print(f'Выбран файл: {user_file}')

        file_obj = File(FILE_FOLDER, user_file)

        # Поменяем таблицу для записи
        current_model = WorkWithStatistic.get_next_model_obj(APP_NAME)

        # Пересоздадим таблицу в БД для модели, которую будем сейчас использовать
        RebuildDataParseModel.for_model(current_model)

        print(f'Начинаем обрабатывать файл: {file_obj.file_name}...')

        row_counter = 0
        temp_line = []
        for line in tqdm(tuple(WorkWithXLSXFiles.get_lxsx_file_line_iterator(file_obj))):
            # Если строку сначала файла не нужно обрабатывать - то пропускаем
            if row_counter < EXCLUDE_COUNT_OF_LINES_FROM_FILE:
                row_counter += 1
                continue

            # # -------------------------------------------
            #     print(line)
            #     row_counter += 1
            #
            #     if row_counter == 39:
            #         break
            #
            # # -------------------------------------------

            # Поместим данные строки в ДТО
            try:
                # Если есть ФИО, то сохраняем строку для подстановки в следующие пустые строки
                if line[0] and line[1] and line[2] and line[10] and line[11] and line[12]:
                    temp_line = line
                # Если это строка - где второй номер телефона, то просто пропустим его
                if line[0] == '' and line[1] == '' and line[2] == '' and line[14] == '' and line[15] == '' and line[
                    16] == '':
                    continue
                # Если ФИО пусты но есть даты расчетного периода и сумма, то добавим в строку предидущие ФИО
                if line[0] == '' and line[1] == '' and line[2] == '' and line[14] and line[15]:
                    line_2 = temp_line[0:14]
                    line_2.append(line[14])
                    line_2.append(line[15])
                    line_2.append(line[16])
                    line = line_2
                if line[0] == '' and line[1] == '' and line[2] == '':
                    print('!!! ', line)

                row_dto = CURRENT_DTO(
                    last_name=line[0],
                    first_name=line[1],
                    patronymic=line[2],
                    date_of_birth=line[3],
                    snils=line[4],
                    division=line[5],
                    adress=line[6],
                    phones=line[7],
                    date_of_initial_appeal=line[8],
                    date_registration_as_unemployed=line[9],
                    payment_start_date=line[10],
                    payment_end_date=line[11],
                    name_of_the_payment=line[12],
                    date_de_registration_as_unemployed=line[13],
                    date_start_billing_period=line[14],
                    date_end_billing_period=line[15],
                    amount_accrued=line[16]
                )
            except Exception as error:
                if VERBOSE:
                    print(' Ошибка добавления в DTO '.center(69, '-'))
                    error_type, error_value, error_trace = sys.exc_info()
                    print("Type: ", error_type)
                    print("Value:", error_value)
                    print("Trace:", error_trace)
                    traceback.print_exception(error_type, error_value, error_trace, limit=5, file=sys.stdout)
                    print('-'.center(69, '-'))
                current_error = f'Ошибка добавления в DTO: {CURRENT_DTO.__name__}. split_line: {line}.'
                SaveParserError.for_registry(
                    registry=APP_NAME,
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
                if VERBOSE:
                    print(' Ошибка ORM '.center(69, '-'))
                    error_type, error_value, error_trace = sys.exc_info()
                    print("Type: ", error_type)
                    print("Value:", error_value)
                    print("Trace:", error_trace)
                    print(f'row_dto.get_data: {dict(**row_dto.get_data)}')
                    traceback.print_exception(error_type, error_value, error_trace, limit=5, file=sys.stdout)
                    print('-'.center(69, '-'))
                current_error = f'Ошибка ORM. len(split_line): {len(line)}. split_line: {line}. **row_dto.get_data: {dict(**row_dto.get_data)}'
                SaveParserError.for_registry(
                    registry=APP_NAME,
                    error_message=error,
                    addition_data=current_error
                )
                continue

            # if row_counter % 100000 == 0:
            #     print(f'Обработано {row_counter} строк...')

            row_counter += 1

        print(f'Всего строк обработано: {row_counter - 1 - EXCLUDE_COUNT_OF_LINES_FROM_FILE}')

        # Сохраним данные статистики о произошелшем процессе парсинга в соотетствующую таблицу
        SaveParseStatistic.for_registry(
            registry=APP_NAME,
            parse_start_date=PARSE_START_DATE,
            parse_end_date=timezone.now(),
            parse_model_name=current_model.__name__,
            parse_number_of_lines=row_counter - 1
        )

        # Сделаем бэкап файла
        backup_file_name = f"{time.time()}_{file_obj.get_file_name}"
        try:
            shutil.copy2(
                file_obj.file_path,
                os.path.join(APP_BACKUP_FOLDER, backup_file_name)
            )
            print(f'Бэкап файла {file_obj.get_file_name} создан.')
        except Exception as error:
            if VERBOSE:
                print(' Ошибка создания бэкапа файла '.center(69, '-'))
                error_type, error_value, error_trace = sys.exc_info()
                print("Type: ", error_type)
                print("Value:", error_value)
                print("Trace:", error_trace)
                traceback.print_exception(error_type, error_value, error_trace, limit=5, file=sys.stdout)
                print('-'.center(69, '-'))

            current_error = f'Ошибка создания бэкапа файла {backup_file_name}.'
            SaveParserError.for_registry(
                registry=APP_NAME,
                error_message=error,
                addition_data=current_error
            )
            print(current_error)
