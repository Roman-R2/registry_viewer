from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from authapp.models import AppExtendedUser, UserAllowedApps


# class AppExtendedUserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'first_name', 'last_name', 'patronymic', 'office')
#     fields = ('username', 'first_name', 'last_name', 'patronymic', 'office', 'password')
#     readonly_fields = [
#         'date_joined',
#     ]


class AppExtendedUserAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'patronymic',
        'office',
        'is_staff',
        'is_superuser',
        'is_active')
    pass


admin.site.register(AppExtendedUser, AppExtendedUserAdmin)
admin.site.register(UserAllowedApps)
