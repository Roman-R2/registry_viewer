from __future__ import annotations

from datetime import datetime, timedelta
from typing import Tuple

from django.conf import settings
from django.db.models import F
from django.utils import timezone

from app.settings_for_apps import REGISTRY_DATA
from authapp.models import AppExtendedUser
from mainapp.dto import FileStatDTO
from mainapp.models import AppCanvasModel
from registry_br.models import RegistryBRBackup1, RegistryBRBackup2
from registry_id.models import RegistryIDBackup1, RegistryIDBackup2
from registry_lrp.models import RegistryLRPBackup1, RegistryLRPBackup2
# from registry_ms.models import RegistryMSBackup1, RegistryMSBackup2
from registry_rtn_ts.models import RegistryRtnTsBackup1, RegistryRtnTsBackup2
from registry_zp.models import RegistryZPBackup1, RegistryZPBackup2
from statisticapp.choices import (ActivityChoices, ErrorTypesChoices,
                                  RegistryNameChoices)
from statisticapp.models import (ParserErrors, ParseStatistics,
                                 UserActivityStatistics,
                                 UserFailedLoginAttempts, ParseFileStat)


class SaveParserError:
    """ Сохранит ошибку в базу данных """

    def __init__(self, registry_name, error_type, error_message, addition_data):
        self.registry_name = registry_name
        self.error_type = error_type
        self.error_message = error_message
        self.addition_data = addition_data

    def _save_to_db(self):
        ParserErrors.objects.create(
            registry_name=self.registry_name,
            error_type=self.error_type,
            error_message=self.error_message,
            addition_data=self.addition_data
        )

    @staticmethod
    def common_record(error_message, addition_data: str):
        return SaveParserError(
            registry_name=RegistryNameChoices.COMMON_RECORD,
            error_type=ErrorTypesChoices.COMMON_RECORD,
            error_message=error_message,
            addition_data=addition_data
        )._save_to_db()

    @staticmethod
    def for_lrp_registry(error_message, addition_data: str):
        return SaveParserError(
            registry_name=RegistryNameChoices.REGISTRY_LRP,
            error_type=ErrorTypesChoices.PARSE_ERROR,
            error_message=error_message,
            addition_data=addition_data
        )._save_to_db()

    @staticmethod
    def for_id_registry(error_message, addition_data: str):
        return SaveParserError(
            registry_name=RegistryNameChoices.REGISTRY_ID,
            error_type=ErrorTypesChoices.PARSE_ERROR,
            error_message=error_message,
            addition_data=addition_data
        )._save_to_db()

    @staticmethod
    def for_registry(registry: str, error_message, addition_data: str):
        return SaveParserError(
            registry_name=registry,
            error_type=ErrorTypesChoices.PARSE_ERROR,
            error_message=error_message,
            addition_data=addition_data
        )._save_to_db()


class SaveParseStatistic:
    """ Сохранит статистику парсинга данных для соответствующих моделей. """

    def __init__(
            self,
            file: FileStatDTO,
            registry_name: str,
            parse_start_date: datetime,
            parse_end_date: datetime,
            parse_model_name: str,
            parse_number_of_lines: int
    ):
        self.file = file
        self.registry_name = registry_name
        self.parse_start_date = parse_start_date
        self.parse_end_date = parse_end_date
        self.parse_number_of_lines = parse_number_of_lines
        self.parse_model_name = parse_model_name
        self.parse_process_count = self._get_last_process_count()

    def _save_to_db(self):
        """ Сохранит информацию в БД. """
        return ParseStatistics.objects.create(
            file=self.file,
            registry_name=self.registry_name,
            parse_start_date=self.parse_start_date,
            parse_end_date=self.parse_end_date,
            parse_model_name=self.parse_model_name,
            parse_number_of_lines=self.parse_number_of_lines,
            parse_process_count=self.parse_process_count + 1
        )

    def _get_last_process_count(self):
        """ Получит последний счетчик обновлений данных для соответствующего регистра."""
        try:
            last_count = ParseStatistics.objects.filter(
                registry_name=self.registry_name
            ).order_by('-parse_process_count').first().parse_process_count
        except AttributeError:
            last_count = 0
        return last_count

    @staticmethod
    def for_registry(
            file: FileStatDTO,
            registry,
            parse_start_date,
            parse_end_date,
            parse_model_name,
            parse_number_of_lines
    ):
        return SaveParseStatistic(
            file=file,
            registry_name=registry,
            parse_start_date=parse_start_date,
            parse_end_date=parse_end_date,
            parse_model_name=parse_model_name,
            parse_number_of_lines=parse_number_of_lines,
        )._save_to_db()


class WorkWithStatistic:
    """ Обеспечивает работу с моделями и данными приложения statisticapp. """

    def __init__(self, registry_name: str):
        self.registry_name = registry_name

    def get_allowed_models(self, name) -> Tuple[AppCanvasModel]:
        """ Вернет разрешенные модели из настроек реестров приложения по внутреннему имени. """
        for registry in REGISTRY_DATA:
            if registry.internal_service_registry_name == name:
                return registry.allowed_models
        raise ValueError(
            f'Не существует разрешенных моделей регистров по переданному внутреннему имени регистра {name}')

    def _get_current_model_name(self):
        """ Получит имя модели, куда была произведена последняя запись. """
        try:
            parse_statistic_obj = ParseStatistics.objects.filter(
                registry_name=self.registry_name
            ).order_by('-parse_process_count').first()
        except:
            parse_statistic_obj = None

        if parse_statistic_obj is None:
            return self.get_allowed_models(name=self.registry_name)[0].__name__

        return parse_statistic_obj.parse_model_name

    def _get_next_obj(self):
        """ Получит объект следующей модели, куда нужно произвести следующую запись. """
        current_model_name = self._get_current_model_name()
        # print(f'{current_model_name=}')
        if self.get_allowed_models(name=self.registry_name)[0].__name__ == current_model_name:
            current_model = self.get_allowed_models(name=self.registry_name)[1]
        else:
            current_model = self.get_allowed_models(name=self.registry_name)[0]
        return current_model

    def _get_current_obj(self):
        """ Получит объект текущей модели, для ее воспроизведения. """
        current_model_name = self._get_current_model_name()
        if self.get_allowed_models(name=self.registry_name)[0].__name__ == current_model_name:
            current_model = self.get_allowed_models(name=self.registry_name)[0]
        else:
            current_model = self.get_allowed_models(name=self.registry_name)[1]
        return current_model

    @staticmethod
    def get_next_model_obj(registry_name: str):
        """ Получит объект модели переданного реестра, куда была произведена последняя запись. """
        return WorkWithStatistic(registry_name=registry_name)._get_next_obj()

    @staticmethod
    def get_current_model_obj(registry_name: str):
        """ Получит объект модели переданного реестра, куда была произведена последняя запись. """
        return WorkWithStatistic(registry_name=registry_name)._get_current_obj()


class SaveUserActivityStatistics:
    """ Сохранит статистику по действиям пользователя в приложении. """

    def __init__(self, user: AppExtendedUser | None, user_ip: str, activity: ActivityChoices, addition_data: str):
        self.user = user
        self.user_ip = user_ip
        self.activity = activity
        self.addition_data = addition_data

    def _save_to_db(self):
        """ Сохранит информацию в БД. """
        UserActivityStatistics.objects.create(
            user=self.user,
            user_ip=self.user_ip,
            activity=self.activity,
            addition_data=self.addition_data
        )

    @staticmethod
    def with_data(user: AppExtendedUser, user_ip: str, activity, addition_data: str):
        return SaveUserActivityStatistics(
            user=user,
            user_ip=user_ip,
            activity=activity,
            addition_data=addition_data
        )._save_to_db()


class WorkUserFailedLoginAttempts:
    """ Работа с неудачными попытками входа ползователя в приложение. """

    def __init__(self, user_name: str):
        self.user_name = user_name

    def _process(self):
        """ Проверит, что такое имя пользователя есть в БД и если есть, добавит запись в БД. """
        user = self.__get_user_or_none()
        if user:
            self._work_with_db(user)

    def __get_user_or_none(self):
        """ Вернет пользователя или none, если его не существует """
        try:
            return AppExtendedUser.objects.get(username=self.user_name)
        except:
            return None

    def get_user_failed_login_attempts_or_none(self, user: AppExtendedUser):
        """ Вернет пользователя или none, если его не существует """
        try:
            return UserFailedLoginAttempts.objects.filter(user=user).order_by('-updated_at').first()
        except:
            return None

    def _reset_login_attempts(self, user: AppExtendedUser):
        """ Обнулит неудачные попытки входа в пользователя. """
        user_failed_login_attempts = self.get_user_failed_login_attempts_or_none(user=user)
        if user_failed_login_attempts:
            UserFailedLoginAttempts.objects.update(
                user=user,
                number_of_failed_attempts=0,
                expired_date=None
            )
        else:
            UserFailedLoginAttempts.objects.create(
                user=user,
                number_of_failed_attempts=0,
                expired_date=None
            )

    def _is_blocked_user(self):
        """ Проверит, что пользователь заблокирован. """
        user = self.__get_user_or_none()
        if user:
            user_login_row = UserFailedLoginAttempts.objects.all().filter(user_id=user).order_by('-updated_at').first()
            if user_login_row and user_login_row.expired_date:
                if user_login_row.expired_date < timezone.now():
                    return False
                else:
                    return True
            else:
                return False
        else:
            return False

    # def _block_user(self, user: AppExtendedUser):
    #     """ Сделает пользователя неактивным. """
    #     AppExtendedUser.objects.get(username=user)
    #     user.is_active = False
    #     user.save()

    def _work_with_db(self, user: AppExtendedUser):
        """ Возьмет в БД информацию по данному пользователю, ести она есть
        и сохранит в статистику данные о неудачной попытке въхода. """

        user_failed_login_attempts = self.get_user_failed_login_attempts_or_none(user=user)

        if user_failed_login_attempts is not None:

            count_of_user_attempts = user_failed_login_attempts.number_of_failed_attempts

            if count_of_user_attempts >= settings.MAX_NUMBER_OF_LOGIN_ATTEMPTS - 1:
                # self._block_user(user)

                user_failed_login_attempts.expired_date = datetime.now() + timedelta(
                    minutes=settings.BLOCK_LOGIN_IN_MINUTES_AFTER_FAILED_ATTEMPTS
                )

                user_failed_login_attempts.save()

                SaveUserActivityStatistics.with_data(
                    user=user,
                    user_ip='',
                    activity=ActivityChoices.USER_BLOCK,
                    addition_data=f'Пользователь user.username={user.username} Заблокирован после {settings.MAX_NUMBER_OF_LOGIN_ATTEMPTS} попыток входа в приложение'
                )
            else:
                user_failed_login_attempts.number_of_failed_attempts = F('number_of_failed_attempts') + 1
                user_failed_login_attempts.save()
        else:
            UserFailedLoginAttempts.objects.create(
                user=user,
                number_of_failed_attempts=1
            )

            # if user_failed_login_attempts:
            #     UserFailedLoginAttempts.objects.update(
            #         user=user,
            #         number_of_failed_attempts=user_failed_login_attempts.number_of_failed_attempts + 1
            #     )
            # else:
            #     UserFailedLoginAttempts.objects.create(
            #         user=user,
            #         number_of_failed_attempts=1
            #     )

    @staticmethod
    def with_data(user_name: str):
        return WorkUserFailedLoginAttempts(
            user_name=user_name,
        )._process()

    @staticmethod
    def reset_login_attempts(user: AppExtendedUser):
        return WorkUserFailedLoginAttempts(
            user_name=user.username,
        )._reset_login_attempts(user)

    @staticmethod
    def is_blocked_user(user_name: str):
        return WorkUserFailedLoginAttempts(
            user_name=user_name,
        )._is_blocked_user()

    @staticmethod
    def get_user_or_none(user_name: str):
        """ Вернет объект пользователя или None. """
        return WorkUserFailedLoginAttempts(
            user_name=user_name,
        ).__get_user_or_none()
