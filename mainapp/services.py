import os
from pathlib import Path
from zipfile import ZipFile

import pylightxl as xl
from django.conf import settings
from django.db import ProgrammingError, connection
from django.shortcuts import render

from app.settings_for_apps import REGISTRY_DATA
from authapp.models import UserAllowedApps
from statisticapp.models import UserFailedLoginAttempts
from statisticapp.services import SaveParserError


class File:
    """ Содержит данные файла и проверит файл ли это."""

    def __init__(self, file_dir: str, file_name: str):
        self.file_name = file_name
        self.file_path = os.path.join(file_dir, file_name)
        self.__check_file()

    def __check_file(self):
        """ Проверит файл ли это. Если не файл то запишет ошибку в БД. """
        if os.path.isfile(self.file_path):
            self.file_path = self.file_path
        else:
            current_error = f"Ошибка! Файл: {self.file_path} - Такого файла нет, или это не файл."
            SaveParserError.common_record(
                error_message='',
                addition_data=current_error
            )
            raise ValueError(current_error)

    @property
    def get_file_path(self):
        """ Вернет полный путь до файла в виде строки. """
        return self.file_path

    @property
    def get_file_name(self):
        """ Вернет имя файла в виде строки. """
        return self.file_name


class ProcessZipFile:
    """ Извлечет нужный файл из zip-архива. """

    def __init__(self, zip_file: File, extraction_dir: str):
        self.zip_file = zip_file
        self.extraction_dir = extraction_dir

    def __check_file_count(self, list_of_zip_files: list):
        if len(list_of_zip_files) > 1:
            current_error = f"Ошибка! Файлов в zip архиве больше, чем 1.\n " \
                            f"Список файлов: {list_of_zip_files} \n " \
                            f"extraction_dir: {self.extraction_dir}"
            SaveParserError.common_record(
                error_message='',
                addition_data=current_error
            )
            raise FileExistsError(current_error)

    @property
    def extract_file_from_zip(self):
        with ZipFile(self.zip_file.get_file_path) as current_zip:
            files_list = current_zip.filelist
            self.__check_file_count(files_list)
            try:
                # Распакуем файл в указанную директорию
                current_zip.extract(files_list[0], path=self.extraction_dir)
            except FileExistsError as error:
                current_error = 'Zip файл не распоковался...'
                SaveParserError.common_record(
                    error_message=error,
                    addition_data=current_error
                )
                print(current_error)
            return files_list[0].filename


class ProcessZipFileV2:
    """ Извлечет нужный файл из zip-архива. """

    def __init__(self, zip_file: Path, extraction_dir: str):
        self.zip_file = zip_file
        self.extraction_dir = extraction_dir

    def __check_file_count(self, list_of_zip_files: list):
        if len(list_of_zip_files) > 1:
            current_error = f"Ошибка! Файлов в zip архиве больше, чем 1.\n " \
                            f"Список файлов: {list_of_zip_files} \n " \
                            f"extraction_dir: {self.extraction_dir}"
            SaveParserError.common_record(
                error_message='',
                addition_data=current_error
            )
            raise FileExistsError(current_error)

    @property
    def extract_file_from_zip(self):
        with ZipFile(self.zip_file) as current_zip:
            files_list = current_zip.filelist
            self.__check_file_count(files_list)
            try:
                # Распакуем файл в указанную директорию
                current_zip.extract(files_list[0], path=self.extraction_dir)
            except FileExistsError as error:
                current_error = 'Zip файл не распоковался...'
                SaveParserError.common_record(
                    error_message=error,
                    addition_data=current_error
                )
                print(current_error)
            return files_list[0].filename


class PreprocessingRawString:
    """ Обработает строку по определнным правилам. """

    def __init__(self, string: str):
        self.string = string
        self.start = 0
        self.end = 0
        self.index_set = set()

    def clear_triple_quotes(self):
        """ Заменит тройные кавычки на одинарные. """
        self.string = self.string.replace('"""', '"')

    def clear_square_brackets(self):
        """ Удалит квадратные скобки. """
        self.string = self.string.replace('[', '')
        self.string = self.string.replace(']', '')

    def clear_null_substring(self):
        """ Удалит квадратные скобки. """
        self.string = self.string.replace('(null)', 'null')

    def process(self):
        """ Главная функция обработки строки """
        if len(self.string) == 0:
            return self.string

        self.clear_triple_quotes()
        self.clear_square_brackets()
        self.clear_null_substring()

        # print(self.string)

        while not self.stopping():
            self.start, self.end = self._find_patterning_substring_indexes(self.string)
            print(self.string)
            print(self.start, self.end)
            if not self.stopping():
                self.index_set.add((self.start, self.end))
                left_part = self.string[:self.start]
                center_part = self._process_part_of_string(self.string[self.start: self.end + 1])

                right_part = self.string[self.end + 1:]

                self.string = left_part + center_part + right_part
        return self.string

    def stopping(self):
        return self.start == -1 and self.end == -1

    def _find_patterning_substring_indexes(self, line: str):
        """ Найдет индексы начала и конца подстроки для обработки. """
        start = -1
        end = -1
        for i, char in enumerate(line):
            if line[i] == '"' and line[i - 1] == ';':
                start = i
                break
        for i, char in enumerate(line):
            if line[i] == '"' and line[i + 1] == ';':
                # если старт там же где и конец, то это была строка вида
                # ;";char";
                # поэтому ищем дальше
                if start == i:
                    continue
                end = i
                break
        if start == -1 or end == -1:
            start = -1
            end = -1
        return start, end

    def _process_part_of_string(self, string: str):
        """ Обработает часть строки по входящим параметрам, """
        string = string.replace(';', '')
        string = string.replace('"', '')
        return string


class PreprocessingRawStringV2:
    """ Обработает строку по определнным правилам. """

    def __init__(self, string: str):
        self.string = string

    def __clear_unnecessary_semicolon(self):
        """ Удалит ненужные симполы точки с запятой внутри кавычек. """
        is_opened_quotes = False
        quotes_count = 0
        char_list = []
        continue_again = False
        for i in range(len(self.string)):
            if continue_again:
                quotes_count -= 1
                if quotes_count == 0:
                    continue_again = False
                    is_opened_quotes = False
            if self.string[i] != '"' and not is_opened_quotes:
                char_list.append(self.string[i])
            if self.string[i] != '"' and is_opened_quotes:
                if self.string[i] != ';':
                    char_list.append(self.string[i])
            if self.string[i] == '"' and is_opened_quotes:
                if self.string[i - 1] == '"':
                    if not continue_again:
                        quotes_count += 1
                    char_list.append(self.string[i])
                else:
                    char_list.append(self.string[i])
                    continue_again = True
                    continue
            if self.string[i] == '"' and not is_opened_quotes:
                is_opened_quotes = True
                quotes_count += 1
                char_list.append(self.string[i])

        self.string = ''.join(char_list)

    def __replace_slash_quote(self):
        self.string = self.string.replace(r'\"\"";', '";')
        self.string = self.string.replace(r'\"";', '";')
        self.string = self.string.replace(r'\""', '')
        self.string = self.string.replace(r'\"', '')

    def __clear_triple_quotes(self):
        """ Заменит тройные кавычки на одинарные. """
        self.string = self.string.replace('"""', '"')

    def __clear_all_quotes(self):
        """ Заменит тройные кавычки на одинарные. """
        self.string = self.string.replace('"', '')

    def __clear_square_brackets(self):
        """ Удалит квадратные скобки. """
        self.string = self.string.replace('[', '')
        self.string = self.string.replace(']', '')

    def __clear_null_substring(self):
        """ Удалит квадратные скобки. """
        self.string = self.string.replace('(null)', 'null')

    def __clear_manu_quotes_with_empty(self):
        self.string = self.string.replace(';"";', ';;')
        self.string = self.string.replace(';"""""";', ';;')

    def __clear_double_slash(self):
        self.string = self.string.replace(r'\\"', '"')
        self.string = self.string.replace(r'\\', '')

    def __replace_random_unique_phrases(self):
        # self.string = self.string.replace('без серии \\', 'без серии')
        # self.string = self.string.replace('без номера\\', 'без номера')
        # self.string = self.string.replace('\\"Медынский район\\"', 'Медынский район')
        # self.string = self.string.replace('\\"Тигильский муниципальный район\\"', 'Тигильский муниципальный район')
        pass

    def __main_processor(self):
        """ Главный метод, который запускает другие обработки строки. """

        self.__replace_random_unique_phrases()
        self.__clear_double_slash()
        self.__clear_manu_quotes_with_empty()
        self.__replace_slash_quote()
        self.__clear_unnecessary_semicolon()
        self.__clear_all_quotes()
        self.__clear_square_brackets()
        self.__clear_null_substring()

        return self.string

    @staticmethod
    def process(string):
        return PreprocessingRawStringV2(string).__main_processor()


class RebuildDataParseModel:
    """ Удалит выбранную по модели таблицу из БД и создаст ее заново. """

    def __init__(self, model_for_rebuild: str):
        self.model_for_rebuild = model_for_rebuild

    def _delete_model(self):
        """ Удалит из БД таблицу и данные. """
        with connection.schema_editor() as schema_editor:
            try:
                schema_editor.delete_model(self.model_for_rebuild)
            except ProgrammingError:
                pass

    def _create_model(self):
        """ Создаст в БД таблицу. """
        with connection.schema_editor() as schema_editor:
            try:
                schema_editor.create_model(self.model_for_rebuild)
            except ProgrammingError:
                pass

    def _rebuild_model(self):
        """ Сначала удалит а затем создаст занова таблицу в бд по модели. """
        self._delete_model()
        self._create_model()

    @staticmethod
    def for_model(model_for_rebuild):
        return RebuildDataParseModel(model_for_rebuild=model_for_rebuild)._rebuild_model()


def get_allowed_apps(request):
    """ Вернет список имен доступных пользователю приложений """
    opportunities_apps_obj = UserAllowedApps.objects.filter(user=request.user).first()
    allowed_apps = []
    if opportunities_apps_obj:
        for app in REGISTRY_DATA:
            if eval(f'opportunities_apps_obj.{app.internal_service_registry_name}'):
                allowed_apps.append(app.internal_service_registry_name)

    return allowed_apps


def get_user_opportunities_apps(request):
    """ Вернет список кортежей имен приложений, и значения доступности. """

    user_opportunities = []
    try:
        opportunities_apps_obj = UserAllowedApps.objects.filter(user=request.user).first()

        # Если в БД прописаны разрешения для пользователя, то выбираем,
        # а если не прописаны то все вернем неразрешенное
        if opportunities_apps_obj:
            for app in REGISTRY_DATA:
                user_opportunities.append(
                    (
                        app.internal_service_registry_name,
                        eval(f'opportunities_apps_obj.{app.internal_service_registry_name}')
                    )
                )
        else:
            for app in REGISTRY_DATA:
                user_opportunities.append(
                    (app.internal_service_registry_name, False)
                )

    except TypeError:
        pass

    # print(user_opportunities)
    return user_opportunities


class WorkWithXLSXFiles:
    """ Класс бля работы в файлами формата lxsx. """

    def __init__(self, lxsx_file: Path):
        self.lxsx_file = lxsx_file

    def _get_lxsx_file_line_iterator(self):
        """ Вернет итератор для построчного прохода по файлу. """
        db = xl.readxl(
            fn=str(self.lxsx_file.resolve())
        )

        # Берем первую таблицу из файла
        current_sheet = db.ws_names[0]

        return db.ws(ws=current_sheet).rows

    @staticmethod
    def get_lxsx_file_line_iterator(lxsx_file: Path):
        """ Вернет итератор для построчного прохода по файлу. """
        return WorkWithXLSXFiles(lxsx_file)._get_lxsx_file_line_iterator()


def not_found_404(request):
    return render(
        request,
        'mainapp/errors/404.html',
        status=404,
        context={}
    )


def server_error_500(request):
    return render(
        request,
        'mainapp/errors/500.html',
        status=500,
        context={}
    )


def permission_denied_403(request):
    return render(
        request,
        'mainapp/errors/403.html',
        status=403,
        context={}
    )


def bad_request_404(request):
    return render(
        request,
        'mainapp/errors/400.html',
        status=400,
        context={}
    )


def user_blocked_403(request):
    return render(
        request,
        'mainapp/errors/user_blocked_403.html',
        status=403,
        context={
            'login_block_in_minutes': settings.BLOCK_LOGIN_IN_MINUTES_AFTER_FAILED_ATTEMPTS
        }
    )


class CheckSnils:
    """
    Проверит, является ли переданная строка СНИЛСом.
    Может быть передан в формате 111-111-111 11, либо 11111111111.
    """
    # Граничный СНИЛС для проверки контрольного числа
    BOUND_SNILS = 1001998
    # Максимальное количество повторений цифр для СНИЛС
    MAX_CHAR_REPEAT = 2

    def __init__(self, snils: str):
        self.snils = self.__clear_snils(snils)

    def __clear_snils(self, snils: str):
        """ Очистит строку СНИЛСа, оставив только цифры. Вернет очищенную строку. """
        if '-' in snils:
            snils = snils.replace('-', '')
            snils = snils.replace(' ', '')
        return snils

    def __checking_the_checksum(self):
        """ Проверка контрольного числа СНИЛС. """
        input_checksum = int(self.snils[-2:])

        count = 1
        estimated_checksum = 0
        for char in reversed(self.snils[:-2]):
            estimated_checksum += int(char) * count
            count += 1

        # print(f'{input_checksum=} {estimated_checksum=} {estimated_checksum%101=}')

        if estimated_checksum < 100:
            return input_checksum == estimated_checksum
        if estimated_checksum == 100 or estimated_checksum == 101:
            return input_checksum == 00
        if estimated_checksum > 101:
            return input_checksum == int(str(estimated_checksum % 101)[-2:])

        return False

    def __repeat_three_times(self):
        """ Проверит, повторяется ли символ три раза подряд в self.snils. """
        char_flag = ''
        char_counter = 0

        for char in self.snils[:-2]:
            if char_flag == char:
                char_counter += 1
            else:
                char_flag = char
                char_counter = 0
            if char_counter > self.MAX_CHAR_REPEAT:
                return True
        return False

    def __is_minimum_snils_number(self):
        """
        Проверим услосие, что СНИЛС меньше этого:
        Проверка контрольного числа проводится только для номеров больше номера 001-001-998.
        """
        return int(self.snils) < self.BOUND_SNILS

    def is_snils(self):
        """
        Проверит, является ли переданная строка СНИЛСом.
        Может быть передан в формате 111-111-111 11, либо 11111111111.
        """

        # Проверим, что передана строка,а не что-то другое
        if not isinstance(self.snils, str):
            return False

        if len(self.snils) == 11 and self.snils.isnumeric():
            # Если в СНИЛС повторяется три раза подряд цифра, то это неправильный СНИЛС
            if self.__repeat_three_times():
                return False
            if self.__is_minimum_snils_number():
                return True
            if self.__checking_the_checksum():
                return True

        return False

    def get_numeric_snils(self):
        """ Вернет СНИЛС в формате int """
        return int(self.snils)

    def get_formated_snils(self):
        """ Вернет отформатированные СНИЛС вида 111-111-111 11"""
        return f'{self.snils[:3]}-{self.snils[3:6]}-{self.snils[6:9]} {self.snils[9:]}'


def center_print(text: str, line_length: int = 79):
    print(f' {text} '.center(line_length, '-'))
