from django.contrib import admin

from statisticapp.models import (ParserErrors, ParseStatistics,
                                 UserActivityStatistics, ParseProcess, UserFailedLoginAttempts)

admin.site.register(ParseProcess)
admin.site.register(ParserErrors)
admin.site.register(ParseStatistics)
admin.site.register(UserActivityStatistics)
admin.site.register(UserFailedLoginAttempts)
