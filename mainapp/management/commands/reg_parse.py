"""
Команда, которая запустит парсинг всех регистров

"""

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('registry_lrp_process')
        call_command('registry_zp_process')
        call_command('registry_id_process')
