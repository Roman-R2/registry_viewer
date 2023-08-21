from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand

from mainapp.services import WorkWithXLSXFiles
from statisticapp.services import WorkWithStatistic


class Command(BaseCommand):
    help = 'Переведет данные из excel в модель'

    EXCEL_FILE = settings.BASE_DIR / 'data' / 'source_files' / 'deti_data.xlsx'

    model = WorkWithStatistic.get_current_model_obj('registry_state_support')

    def handle(self, *args, **options):
        print(f"Начали...")
        lxsx_line_iterator = tuple(WorkWithXLSXFiles.get_lxsx_file_line_iterator(self.EXCEL_FILE))

        for item in lxsx_line_iterator:
            self.model.objects.create(
                adult_snils=item[3].strip(),
                adult_fio=f"{item[0].strip()} {item[1].strip()} {item[2].strip()}",
                child_snils=item[8].strip(),
                child_fio=f"{item[4].strip()} {item[5].strip()} {item[6].strip()}",
                child_birthdate=datetime.strptime(item[7].strip(), "%Y/%m/%d").strftime('%Y-%m-%d'),
                child_start_support_date=datetime.strptime(item[9].strip(), "%Y/%m/%d").strftime('%Y-%m-%d'),
                child_location=item[10].strip(),
                child_status=item[11].strip(),
                another_adult_snils=item[13].strip(),
                another_adult_fio=item[12].strip().replace('  ', ' '),
            )
        print(f"Закончили...")
