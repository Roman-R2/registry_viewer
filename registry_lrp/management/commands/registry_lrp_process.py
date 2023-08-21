import shutil
import time

from django.conf import settings
from django.core.management import BaseCommand
import os

from tqdm import tqdm

from django.utils import timezone

from registry_lrp.dto import RegistryLrpDTO
from mainapp.services import ProcessZipFile, File, PreprocessingRawString, RebuildDataParseModel, \
    PreprocessingRawStringV2
from statisticapp.choices import RegistryNameChoices
from statisticapp.services import SaveParserError, SaveParseStatistic, WorkWithStatistic


class Command(BaseCommand):
    def handle(self, *args, **options):
        CURRENT_DTO = RegistryLrpDTO
        REGISTRY_CHOICE_MARK = RegistryNameChoices.REGISTRY_LRP
        APP_NAME = 'registry_lrp'
        APP_BACKUP_FOLDER = os.path.join(settings.BACKUP_FOLDER, APP_NAME)
        # ZIP_FILE_FOLDER = os.path.join(settings.DATA_DIR, 'source_files')
        ZIP_FILE_FOLDER = os.path.join(r'\\10.27.0.14\shdir\post')
        EXTRACTION_DIR = os.path.join('data', 'extracted_files')
        ZIP_FILE_NAME = '27_rlirp.zip'
        PARSE_START_DATE = timezone.now()

        zip_file_obj = File(ZIP_FILE_FOLDER, ZIP_FILE_NAME)

        # raise SystemExit(1)

        # Поменяем таблицу для записи
        current_model = WorkWithStatistic.get_next_model_obj(REGISTRY_CHOICE_MARK)

        # Пересоздадим таблицу в БД для модели, которую будем сейчас использовать
        RebuildDataParseModel.for_model(current_model)

        process_zip_file_obj = ProcessZipFile(
            zip_file_obj,
            EXTRACTION_DIR
        )

        extract_file_name = process_zip_file_obj.extract_file_from_zip

        print(f'Распаковали файл {extract_file_name}...')

        counter_dto_parse_errors = 0
        counter_orm_parse_errors = 0

        with open(os.path.join(EXTRACTION_DIR, extract_file_name), mode='r') as csv_file:
            row_counter = 0
            for line in tqdm(tuple(csv_file)):

                # Если заголовок, то пропускаем
                if row_counter == 0:
                    row_counter += 1
                    continue

                # print(line)

                processed_line = PreprocessingRawStringV2.process(line)
                # print(processed_line)
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
                    print('Произошла ошибка парсинга: ')
                    print(f'\nline: {line}')
                    print(f'processed_line: {processed_line}')
                    print(f'split_line: {split_line}')
                    break

                try:
                    row_dto = CURRENT_DTO(
                        **prepared_dict
                    )
                except Exception as error:
                    current_error = f'Ошибка добавления в DTO: {CURRENT_DTO.__name__}. split_line: {split_line}. len(prepared_dict): {len(prepared_dict)}, prepared_dict: {prepared_dict}'
                    print('--->', current_error)
                    SaveParserError.for_registry(
                        registry=REGISTRY_CHOICE_MARK,
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
                    current_error = f'Ошибка ORM. \n' \
                                    f'line: {line}\n' \
                                    f'len(split_line): {len(split_line)}.\n' \
                                    f'split_line: {split_line}.\n' \
                                    f'len(**row_dto.get_data): {len(dict(**row_dto.get_data))}\n' \
                                    f'**row_dto.get_data: {dict(**row_dto.get_data)}'
                    print('\n', '-' * 70)
                    print(current_error)
                    SaveParserError.for_registry(
                        registry=REGISTRY_CHOICE_MARK,
                        error_message=error,
                        addition_data=current_error
                    )
                    counter_orm_parse_errors += 1
                    continue

                row_counter += 1

        print(f'Всего строк обработано: {row_counter - 1} шт.')
        print(f'Ошибок добавления в DTO: {counter_dto_parse_errors} шт.')
        print(f'Ошибок ORM: {counter_orm_parse_errors} шт.')

        # Сохраним данные статистики о произошелшем процессе парсинга в соотетствующую таблицу
        SaveParseStatistic.for_registry(
            registry=REGISTRY_CHOICE_MARK,
            parse_start_date=PARSE_START_DATE,
            parse_end_date=timezone.now(),
            parse_model_name=current_model.__name__,
            parse_number_of_lines=row_counter - 1
        )

        # Сделаем бэкап файла
        backup_file_name = f"{time.time()}_{zip_file_obj.get_file_name}"
        try:
            shutil.copy2(
                zip_file_obj.file_path,
                os.path.join(APP_BACKUP_FOLDER, backup_file_name)
            )
        except Exception as error:
            current_error = f'Ошибка создания бэкапа файла {backup_file_name}'
            SaveParserError.for_registry(
                registry=REGISTRY_CHOICE_MARK,
                error_message=error,
                addition_data=current_error
            )
