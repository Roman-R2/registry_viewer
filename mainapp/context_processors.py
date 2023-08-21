from datetime import datetime

import psutil

from app.settings_for_apps import REGISTRY_DATA
from mainapp.dto import LinkMenuDTO
from mainapp.services import get_allowed_apps
from statisticapp.models import ParseProcess, ParseStatistics


def link_context_processor(request):
    """ Формирует список ссылок на разрешенные приложения """
    if request.user.is_authenticated:
        user_allowed_apps = get_allowed_apps(request)

        compiled_links_data = []
        for item in REGISTRY_DATA:
            # Если настройки нет в разрешенном списке, то пропустим ее
            if item.internal_service_registry_name not in user_allowed_apps:
                continue

            registry_last_parse_date = ParseStatistics.objects.filter(
                registry_name=item.internal_service_registry_name
            ).order_by('-parse_end_date').first()

            compiled_links_data.append(
                LinkMenuDTO(
                    registry_short_name=item.short_registry_name,
                    registry_description=item.long_registry_name,
                    registry_last_parse_date=registry_last_parse_date.parse_end_date if registry_last_parse_date else [],
                    internal_service_registry_name=item.internal_service_registry_name
                )
            )

        return {
            'compiled_links_data': compiled_links_data,
        }
    return {}


def parse_process_context_processor(request):
    if request.user.is_authenticated:
        process_info = None
        is_parser_process_exists = None

        if request.user.is_superuser:
            last_parser_process = ParseProcess.objects.all().order_by('-started_at').first()
            is_parser_process_exists = psutil.pid_exists(last_parser_process.pid)

            process_info = {}
            if is_parser_process_exists:
                try:
                    p = psutil.Process(pid=last_parser_process.pid).as_dict()
                    process_info['create_time'] = datetime.fromtimestamp(p['create_time'])
                    process_info['name'] = p['name']
                    process_info['pid'] = p['pid']
                    process_info['cpu_percent'] = p['cpu_percent']
                    process_info['cmdline'] = p['cmdline']
                except Exception:
                    pass

        return {
            'is_parser_process_exists': is_parser_process_exists,
            'process_info': process_info
        }
    return {}
