import locale
import math
from datetime import datetime

from django import template
from django.conf import settings
from django.utils import timezone

register = template.Library()


@register.filter
def custom_format_date(date: datetime):
    try:
        if date is None:
            return "-"

        locale.setlocale(locale.LC_ALL, settings.LANGUAGE_CODE)
        now = datetime.now()

        if date.strftime('%d %B %Y') == now.strftime('%d %B %Y'):
            return date.astimezone(timezone.localtime().tzinfo).strftime('сегодня в %H:%M')
        else:
            return date.astimezone(timezone.localtime().tzinfo).strftime('%d %B %Y в %H:%M')
    except Exception:
        return "-"


@register.filter
def get_true_file_size(size_in_bytes: int):
    """ Вернет понятноый размер файла. """
    if size_in_bytes is None or size_in_bytes == 0:
        return "0B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    try:
        i = int(math.floor(math.log(size_in_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_in_bytes / p, 2)
        return f"{s} {size_name[i]}"
    except TypeError as error:
        return f"{error}"

