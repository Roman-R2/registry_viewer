import os.path
import shutil
from collections import namedtuple
from datetime import datetime

from django.conf import settings
from django.db.models import QuerySet


class Transliterate:
    def __init__(self, string):
        self.string = string

    def get_latin(self):
        """ Вернет транскрипцию латиницей. """
        symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                   u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")

        tr = {ord(a): ord(b) for a, b in zip(*symbols)}

        return self.string.translate(tr)


class DeleteFileOrNone:
    def __init__(self, some_file):
        self.some_file = some_file

    def delete(self):
        try:
            os.remove(self.some_file)
        except FileNotFoundError:
            pass


class AddLRPQuerysetToDocumentDotXML:
    DATE = datetime.now().strftime("%d-%m-%Y")

    DOCX_FILE_EXTENSION = 'docx'

    ZIP_FILE_EXTENSION = 'zip'

    DOCUMENT_XML_INPUT_TEMPLATE_FILE = os.path.join(
        settings.DOCX_TEMPLATE_FOLDER_PATH,
        r'lrp_templates\input_templates\word\document.xml'
    )

    DOCUMENT_XML_OUTPUT_TEMPLATE_FILE = os.path.join(
        settings.DOCX_TEMPLATE_FOLDER_PATH,
        r'lrp_templates\output_templates\word\document.xml'
    )

    OUTPUT_FOLDER_PATH = os.path.join(settings.DOCX_OUTPUT_FOLDER_PATH, 'lrp_docx_extract')

    def __init__(
            self,
            queryset: QuerySet
    ):
        self.queryset = queryset
        self.queryset_length = len(queryset)
        self.output_file_name = f'{self.DATE} - Выписка из реестра ЛРП на {queryset[0].adult_snils} - {queryset[0].adult_fio}'
        self.adult_fio = queryset[0].adult_fio
        self.adult_snils = queryset[0].adult_snils
        # print(f'{self.queryset_length} ::: {self.queryset}')

    def __set_replacement_template(self):
        """ Определит именованный кортеж для шаблона замены строк в document.xml. """
        ReplacementTemplate = namedtuple('ReplacementTemplate', [
            'adult_fio',
            'adult_snils',
            'current_date',
            'child_fio',
            'child_snils',
            'child_record_type',
            'child_doc_series',
            'child_doc_number',
            'child_doc_dep',
            'child_doc_start_date',
        ])
        return ReplacementTemplate(
            '{{adult_fio}}',
            '{{adult_snils}}',
            '{{current_date}}',
            '{{child_fio}}',
            '{{child_snils}}',
            '{{child_record_type}}',
            '{{child_doc_series}}',
            '{{child_doc_number}}',
            '{{child_doc_dep}}',
            '{{child_doc_start_date}}'
        )

    def process(self):
        """
        Получить результирующий DOCX-файл и вернет кортеж
        (папка результирующего файла, имя результирующего файла, имя файла для загрузки)
        """
        self.__add_data_in_template()
        self.__create_output_docx()

        return (
            self.OUTPUT_FOLDER_PATH,
            f'{self.output_file_name}.{self.DOCX_FILE_EXTENSION}',
            self.__get_filename_for_download()
        )

    def __get_filename_for_download(self):
        """ Получил имя файла для загрузки через запрос с учетом особенностей загрузкию. """
        file_name_for_download = f'{self.DATE}_LRP_extraction_{self.adult_snils}_{self.adult_fio}.docx'
        for r in ((' ', '_'), ('-', '_')):
            file_name_for_download = file_name_for_download.replace(*r)
        return Transliterate(file_name_for_download).get_latin()

    def __add_data_in_template(self):
        """ Добавит данные из queryset в шаблон document.xml. """
        replacement_template = self.__set_replacement_template()

        with open(
                self.DOCUMENT_XML_INPUT_TEMPLATE_FILE, mode='r', encoding='utf-8'
        ) as input_template_xml, open(
            self.DOCUMENT_XML_OUTPUT_TEMPLATE_FILE, mode='w', encoding='utf-8'
        ) as output_template_xml:
            buffer = []
            buffer_start = False
            for line in input_template_xml:
                if '{{loop_1_start}}' in line:
                    buffer_start = True
                    continue
                if '{{loop_1_end}}' in line:
                    buffer_start = False
                    for i in range(self.queryset_length):
                        for buffer_line in buffer:
                            if replacement_template.child_fio in buffer_line:
                                buffer_line = buffer_line.replace(replacement_template.child_fio,
                                                                  str(self.queryset[i].child_fio)).replace('None', '')
                            if replacement_template.child_snils in buffer_line:
                                buffer_line = buffer_line.replace(replacement_template.child_snils,
                                                                  str(self.queryset[i].child_snils)).replace('None', '')
                            if replacement_template.child_record_type in buffer_line:
                                buffer_line = buffer_line.replace(
                                    replacement_template.child_record_type,
                                    str(self.queryset[i].event_type_code.code_transcript)
                                ).replace('None', '')
                            if replacement_template.child_doc_series in buffer_line:
                                buffer_line = buffer_line.replace(
                                    replacement_template.child_doc_series,
                                    str(self.queryset[i].series_of_document)
                                ).replace('None', '')
                            if replacement_template.child_doc_number in buffer_line:
                                buffer_line = buffer_line.replace(
                                    replacement_template.child_doc_number,
                                    str(self.queryset[i].document_number)
                                ).replace('None', '')
                            if replacement_template.child_doc_dep in buffer_line:
                                buffer_line = buffer_line.replace(
                                    replacement_template.child_doc_dep,
                                    str(self.queryset[i].issuing_authority)
                                ).replace('None', '')
                            if replacement_template.child_doc_start_date in buffer_line:
                                buffer_line = buffer_line.replace(
                                    replacement_template.child_doc_start_date,
                                    str(self.queryset[i].document_date)
                                ).replace('None', '')
                            output_template_xml.write(buffer_line)
                    continue
                if replacement_template.adult_fio in line:
                    line = line.replace(replacement_template.adult_fio, str(self.queryset[0].adult_fio))
                if replacement_template.adult_snils in line:
                    line = line.replace(replacement_template.adult_snils, str(self.queryset[0].adult_snils))
                if replacement_template.current_date in line:
                    line = line.replace(replacement_template.current_date, datetime.today().strftime('%d.%m.%Y'))

                if buffer_start:
                    buffer.append(line)
                else:
                    output_template_xml.write(line)

    def __create_output_docx(self):
        """
        Создаст DOCX-файл с данными, добавленными в шаблон.
        Сделает из подготовленной папки с файлами архив а затем docx файл.
        """
        sh_obj = shutil.make_archive(
            os.path.join(self.OUTPUT_FOLDER_PATH, self.output_file_name),
            self.ZIP_FILE_EXTENSION,
            os.path.join(settings.DOCX_TEMPLATE_FOLDER_PATH, r'lrp_templates\output_templates')
        )

        path_with_docx_extension = os.path.splitext(sh_obj)[0] + '.' + self.DOCX_FILE_EXTENSION

        # Удилим DOCX файл, если он уже был
        DeleteFileOrNone(path_with_docx_extension).delete()

        # Поменяем расширение нафла на DOCX
        os.rename(sh_obj, path_with_docx_extension)
