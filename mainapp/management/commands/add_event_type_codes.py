# """
# Команда для добавления кодов типа события в модель
# """
# from django.conf import settings
# from django.core.management import BaseCommand
#
# from mainapp.models import EventTypeCodes
#
#
# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         for code in settings.EVENT_TYPE_CODES:
#             obj, is_created = EventTypeCodes.objects.get_or_create(
#                 code=code[0],
#                 code_transcript=code[1],
#             )
#             if is_created:
#                 print(f'Добавлен код типа события: {code[0]} -  {code[1]}')
#             else:
#                 print(f'Код уже существует: {code[0]} -  {code[1]}')
#
#         pass
