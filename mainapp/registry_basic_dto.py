from datetime import datetime

from mainapp.custom_loggers import AutoParseLogger
from mainapp.models import EventTypeCodes
from statisticapp.choices import RegistryNameChoices
from statisticapp.services import SaveParserError

LOGGER = AutoParseLogger().get_logger()


class DTOBasic:
    """ Базовый класс, содержащий основные методы для DTO. """

    def _event_type_code_to_obj(self, event_type_code: str, registry: RegistryNameChoices):
        """ Преобразует строку кода типа в число и вернет объект модели EventTypeCodes. """
        CODE_NOT_FOUND = 0

        try:
            event_type_code_in_int = int(event_type_code)
        except ValueError as error:
            current_error = f'Ошибка преобразования кода типа в число. Переданная строка: event_type_code={event_type_code}'
            SaveParserError.for_registry(
                registry=registry,
                error_message=error,
                addition_data=current_error
            )
            return EventTypeCodes.objects.get(code=CODE_NOT_FOUND)

        event_type_codes_obj = EventTypeCodes.objects.filter(code=event_type_code_in_int).first()

        if not event_type_codes_obj:
            current_error = f'Не найден кода типа. Переданный код: event_type_code_in_int={event_type_code_in_int}'
            LOGGER.error(current_error)
            SaveParserError.for_registry(
                registry=registry,
                error_message='',
                addition_data=current_error
            )
            return EventTypeCodes.objects.get(code=CODE_NOT_FOUND)

        return EventTypeCodes.objects.filter(code=event_type_code_in_int).first()

    def _prepare_snils(self, snils: str):
        """ Обработает строки и вернет форматированную строку СНИЛС. """
        return f"{snils[0:3]}-{snils[3:6]}-{snils[6:9]} {snils[9:]}"

    def _prepare_document_number(self, document_number: str):
        """ Подготавливает номер документа для передачи в БД. """
        document_number = self._remove_double_quotes(document_number)
        document_number = self._remove_null_string(document_number)
        return document_number

    def _remove_end_of_line_chars(self, string: str):
        """ Удалит из строки наборы символов \n. """
        string = string.replace('\n', '')
        return string

    def _remove_double_quotes(self, string: str):
        """ Удалит двойные ковычки в начале и конце строки. """
        if not len(string):
            return string
        if string[0] == '"':
            string = string[1:]
        if string[-1] == '"':
            string = string[:-1]
        return string

    def _remove_null_string(self, string: str):
        if string == 'null':
            return None
        if string == 'б/н':
            return None
        if string == '0000':
            return None
        if string == 'нет данных':
            return None
        if string == 'нет сведений':
            return None
        if string == 'нет':
            return None
        if string == 'Б/Н':
            return None
        if string == 'Б/С':
            return None
        if string == '0':
            return None
        return string

    def _remowe_last_hyphen(self, string: str):
        """
        Удалит последний дефис из строки СНИЛС.
        Т.е. заменит строку вида "000-000-000-00" на "000-000-000 00"
        """
        SEARCH_CHAR = '-'

        START_INDEX = -1

        last_index = START_INDEX
        for idx, char in enumerate(string):
            if char == SEARCH_CHAR:
                last_index = idx

        if last_index == START_INDEX:
            return string

        string = string[:last_index] + ' ' + string[last_index + 1:]

        return string

    def _correct_date(self, date_string: str):
        """ Скорректирует строку даты искуственно. """
        date_string = date_string.replace('20211', '2021')
        date_string = date_string.replace('20121', '2021')
        date_string = date_string.replace('20212', '2021')
        date_string = date_string.replace('/', '-')
        return date_string

    def _reformat_data(self, date_string: str, delimiter: str = '.'):
        """ Преобразует дату по переданному разделителю """
        if date_string == '':
            return None
        try:
            date_string = datetime.strptime(date_string, "%Y/%m/%d")

        except ValueError:
            try:
                date_string = datetime.strptime(date_string, "%d.%m.%Y")
            except ValueError:
                return None
        except Exception:
            return None
        return date_string

    def _prepare_series_of_document(self, series_of_document: str):
        return self._remove_null_string(series_of_document)

    def _prepare_issuing_authority(self, issuing_authority: str):
        # issuing_authority = self.remove_shielding(issuing_authority)
        issuing_authority = self._remove_double_quotes(issuing_authority)
        return issuing_authority
