from django.contrib import admin

from mainapp.models import EventTypeCodes, AppErrorMessages

admin.site.register(EventTypeCodes)
admin.site.register(AppErrorMessages)
