import os
from datetime import datetime
from pathlib import Path

from tabulate import tabulate
from colorama import Fore, Back, Style


class GetFileChoice:
    """ Предназначен для выбора конкретного файла из указанной папки. """

    def __init__(self, folder: Path, ignore_files=None):
        if ignore_files is None:
            ignore_files = []

        self.folder = folder
        self.folder_files_count = len(os.listdir(self.folder))
        self.list_of_files = [item for item in os.listdir(self.folder) if item not in ignore_files]

    def __is_dir(self):
        if not self.folder.is_dir():
            print(
                Fore.YELLOW,
                f"Указанный путь не является папкой. \nУказан: {self.folder}",
                Style.RESET_ALL
            )
            return False
        return True

    def __is_empty_dir(self):
        if self.folder_files_count == 0:
            print(
                Fore.YELLOW,
                f"В переданной папке нет файлов. \nУказанна папка: {self.folder}",
                Style.RESET_ALL
            )
            return True
        return False

    def __show_choices_table(self):
        """ Покажет таблицу для выбора файла. """
        print(" Выберите файл из папки ".center(79, '-'))
        table = []
        for choice, file in enumerate(self.list_of_files):
            table.append(
                [
                    f'{choice + 1}.',
                    str(file),
                    datetime.utcfromtimestamp(
                        os.stat(self.folder / str(file)).st_ctime
                    ).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.utcfromtimestamp(
                        os.stat(self.folder / str(file)).st_mtime
                    ).strftime('%Y-%m-%d %H:%M:%S')
                ]
            )

        print(tabulate(table, headers=['Номер файла', 'Имя файла', 'Создан', 'Изменен']))

    def __get_file_choice(self) -> Path:
        if self.__is_dir() and not self.__is_empty_dir():

            self.__show_choices_table()

            is_bad_choice = True
            while is_bad_choice:
                try:
                    user_choice = int(input("Введите номер файла: "))
                    choices_file = self.list_of_files[user_choice - 1]
                    is_bad_choice = False
                    return self.folder / str(choices_file)
                except IndexError:
                    print(
                        Fore.RED,
                        f"Неправильно указан номер файла",
                        Style.RESET_ALL
                    )
                except ValueError:
                    print(
                        Fore.RED,
                        f"Выбор файла должен быть указан числом",
                        Style.RESET_ALL
                    )
        else:
            print(
                Fore.RED,
                f"Скрипт не может быть исполнен",
                Style.RESET_ALL
            )
            exit(1)

    @staticmethod
    def from_folder(folder: Path, ignore_files: list):
        return GetFileChoice(folder, ignore_files).__get_file_choice()


if __name__ == '__main__':
    print("Данный файл является частью приложения и должен запускаться как модуль.")
