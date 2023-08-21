import os

import sys
import threading
from datetime import datetime

from pathlib import Path

from time import sleep

import psutil
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage, FileSystemStorage
from django.http import HttpResponseRedirect

from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, FormView

from app.settings_for_db_dump import DB_DUMP_FOLDER
from app.settings_for_registry_auto_parse import AUTO_PARSE_LOG_FILE, AUTO_PARSE_LOG_FOLDER
from authapp.mixins import IsAuthenticatedMixin, IsAdminUserMixin
from command_runner import FOLDER_WITH_REGISTRY_FOR_PROCESS, TXT_FILE_WITH_COMMANDS, CommandRunnerLogger, \
    COMMAND_RUNNER_LOG_FILE
from mainapp.custom_loggers import AutoParseLogger

from mainapp.models import AppErrorMessages
from metricsapp.forms import RegistryUploadFileForm
from statisticapp.models import ParseStatistics, UserActivityStatistics, ParseProcess

LOGGER = AutoParseLogger().get_logger()


class MetricsView(IsAuthenticatedMixin, IsAdminUserMixin, ListView):
    template_name = 'metricsapp/metrics.html'

    def get_queryset(self):
        parse_statistics = ParseStatistics.objects.all().order_by('-parse_end_date')[:20]
        user_activity_statistics = UserActivityStatistics.objects.all().order_by('-created_at')[:100]
        app_error_messages = AppErrorMessages.objects.all()[:10]
        python_info = sys.version_info

        db_dump_folder: Path = DB_DUMP_FOLDER
        db_dump_files = [
            (
                item.name,
                item.stat().st_size,
                datetime.fromtimestamp(item.stat().st_mtime)
            )
            for item in list(db_dump_folder.iterdir())
            if item.name != ".gitkeep" and item.suffix == ".sql"
        ]
        db_dump_common_size = sum([int(item[1]) for item in db_dump_files])

        # print(f"db_dump_files={db_dump_files}")
        # print(f"db_dump_files={sorted(db_dump_files, key=lambda a: a[2], reverse=True)}")

        return {
            'parse_statistic': parse_statistics,
            'db_dump_files': sorted(db_dump_files, key=lambda a: a[2], reverse=True),
            'db_dump_common_size': db_dump_common_size,
            'user_activity': user_activity_statistics,
            'chart_registry_processing': 1,
            'python_info': python_info,
            'app_error_messages': app_error_messages,
        }


def auto_parse_run():
    cmd_str = "python manage.py registry_auto_parse"
    os.system(cmd_str)


class RunAutoParseView(MetricsView):

    def get(self, request, *args, **kwargs):
        last_parser_process = ParseProcess.objects.all().order_by('-started_at').first()
        if psutil.pid_exists(last_parser_process.pid):
            sleep(1)
        else:
            thread = threading.Thread(target=auto_parse_run, daemon=True)
            thread.start()

            # os.system(cmd_str)
            LOGGER.info(
                f'Процесс автоматического парсинга регистров ({thread.name}) '
                f'запущен из web-приложения пользователем {request.user}'
            )
            sleep(1)
        return redirect(reverse('metricsapp:index'))


class StopAutoParseView(MetricsView):
    def get(self, request, *args, **kwargs):
        last_parser_process = ParseProcess.objects.all().order_by('-started_at').first()

        if psutil.pid_exists(last_parser_process.pid):

            auto_parse_process = psutil.Process(pid=last_parser_process.pid)
            auto_parse_process.kill()
            LOGGER.info(
                f'Процесс автоматического парсинга регистров (pid {last_parser_process.pid}) '
                f'остановлен из web-приложения пользователем {request.user}'
            )
        else:
            sleep(1)

        return redirect(reverse('metricsapp:index'))


class IndexView(MetricsView):
    template_name = 'metricsapp/metrics.html'


class AutoParseLogsView(IsAuthenticatedMixin, IsAdminUserMixin, TemplateView):
    template_name = 'metricsapp/auto_parse_logs.html'

    row_items_get_name = 'items'

    def get_context_data(self):
        if self.row_items_get_name in self.request.GET:
            items = int(self.request.GET[self.row_items_get_name])
        else:
            items = 100
        try:
            with AUTO_PARSE_LOG_FILE.open(mode='r', encoding='utf-8') as fd:
                lines = fd.readlines()[::-1][:items]
        except Exception:
            lines = []

        try:
            lines = [
                (
                    item.split(' ')[2],
                    ' '.join(item.split(' ')[:2]),
                    ' '.join(item.split(' ')[3:])
                )
                for item in lines
            ]
        except IndexError:
            lines = [
                (
                    '',
                    '',
                    item
                )
                for item in lines
            ]

        current_log_folder: Path = AUTO_PARSE_LOG_FOLDER

        return {
            'logs': lines,
            'logs_count': items,
            'logs_find_count': len(lines),
            'logs_file_current': AUTO_PARSE_LOG_FILE.name,
            'logs_file_all': [
                item
                for item in current_log_folder.iterdir()
                if item.name != '.gitkeep' and AUTO_PARSE_LOG_FILE.name != item.name
            ],
        }


class AutoParseLogsErrorsView(IsAuthenticatedMixin, IsAdminUserMixin, TemplateView):
    template_name = 'metricsapp/auto_parse_logs.html'

    row_items_get_name = 'items'

    def get_context_data(self):
        if self.row_items_get_name in self.request.GET:
            items = int(self.request.GET[self.row_items_get_name])
        else:
            items = 100
        try:
            with AUTO_PARSE_LOG_FILE.open(mode='r', encoding='utf-8') as fd:
                lines = fd.readlines()[::-1]
                # lines = [item for item in lines if 'ERROR' in item]
            lines = [item for item in lines if item.split(' ')[2] == 'ERROR'][:items]
        except Exception:
            lines = []

        try:
            lines = [
                (
                    item.split(' ')[2],
                    ' '.join(item.split(' ')[:2]),
                    ' '.join(item.split(' ')[3:])
                )
                for item in lines
            ]
        except IndexError:
            lines = [
                (
                    '',
                    '',
                    item
                )
                for item in lines
            ]

        current_log_folder: Path = AUTO_PARSE_LOG_FOLDER

        return {
            'logs': lines,
            'logs_count': items,
            'logs_find_count': len(lines),
            'logs_file_current': AUTO_PARSE_LOG_FILE.name,
            'logs_file_all': [
                item
                for item in current_log_folder.iterdir()
                if item.name != '.gitkeep' and AUTO_PARSE_LOG_FILE.name != item.name
            ],
        }


class AutoParseHelpView(IsAuthenticatedMixin, IsAdminUserMixin, TemplateView):
    template_name = 'metricsapp/help.html'


class ManualParseRegistryBrView(IsAuthenticatedMixin, IsAdminUserMixin, FormView):
    template_name = 'metricsapp/manual_parse_run/registry_br.html'
    form_class = RegistryUploadFileForm
    success_url = reverse_lazy('metricsapp:manual_parse_registry_br_process')
    LOGGER = CommandRunnerLogger().get_logger()

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = request.FILES['file']
            # --- Сохраняем файл в папку для дальнейшей обработки
            file_name = FileSystemStorage(
                location=FOLDER_WITH_REGISTRY_FOR_PROCESS
            ).save(data.name, data)
            self.LOGGER.info(f"Загрузили файл {file_name}")
            # --- Запишем комманду в файл для выполнения
            # Создадим файл, если его нет
            if not TXT_FILE_WITH_COMMANDS.exists():
                TXT_FILE_WITH_COMMANDS.open(mode='x', encoding='utf-8')
                self.LOGGER.info(f"Создали файл хранения комманд {TXT_FILE_WITH_COMMANDS.resolve()}")

            with TXT_FILE_WITH_COMMANDS.open(mode='a', encoding='utf-8') as fd:
                command_for_run = f'python manage.py registry_br_process_v_2 registry_br "{(FOLDER_WITH_REGISTRY_FOR_PROCESS / file_name).resolve()}"'
                fd.write(f"{command_for_run}\n")
                self.LOGGER.info(f"записали комманду {command_for_run}")

            return redirect(self.success_url)
        else:
            return render(request, self.template_name, {'form': form})


class ManualParseRegistryBrProcessView(IsAuthenticatedMixin, IsAdminUserMixin, TemplateView):
    template_name = 'metricsapp/manual_parse_run/registry_br_process.html'

    def get_context_data(self):
        context = super().get_context_data()
        with COMMAND_RUNNER_LOG_FILE.open(mode='r', encoding='utf-8') as fd:
            lines = fd.readlines()

        context['logs'] = lines[::-1][:200]

        return context
