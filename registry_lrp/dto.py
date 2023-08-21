from datetime import datetime
from typing import NamedTuple

from mainapp.registry_basic_dto import DTOBasic
from statisticapp.choices import RegistryNameChoices


class RegistryLrpDTO(DTOBasic):
    """ Содержит данные полей реестра лищенных родительских прав. """

    registry = RegistryNameChoices.REGISTRY_LRP

    def __init__(
            self,
            adult_snils: str,
            child_snils: str,
            adult_fio: str,
            child_fio: str,
            event_type_code: str,
            effective_date: str,
            series_of_document: str,
            document_number: str,
            issuing_authority: str,
            document_date: str,
    ):
        self.adult_snils = self._prepare_snils(adult_snils)
        self.child_snils = self._prepare_snils(child_snils)
        self.adult_fio = adult_fio.title()
        self.child_fio = child_fio.title()
        self.event_type_code = self._event_type_code_to_obj(event_type_code, self.registry)
        self.document_number = self._prepare_document_number(document_number)
        self.effective_date = self._correct_date(effective_date)
        self.series_of_document = self._prepare_series_of_document(series_of_document)
        self.issuing_authority = self._prepare_issuing_authority(issuing_authority)
        self.document_date = self._correct_date(document_date)

    @property
    def get_data(self):
        return {
            'adult_snils': self.adult_snils,
            'child_snils': self.child_snils,
            'adult_fio': self.adult_fio,
            'child_fio': self.child_fio,
            'event_type_code': self.event_type_code,
            'effective_date': self.effective_date,
            'series_of_document': self.series_of_document,
            'document_number': self.document_number,
            'issuing_authority': self.issuing_authority,
            'document_date': self.document_date,
        }


class RegistryIdDTO(DTOBasic):
    """ Содержит данные полей реестра недееспособных. """

    registry = 'registry_id'

    def __init__(
            self,
            adult_snils: str,
            adult_fio: str,
            event_type_code: str,
            effective_date: str,
            series_of_document: str,
            document_number: str,
            issuing_authority: str,
            document_date: str,
    ):
        self.adult_snils = self._prepare_snils(adult_snils)
        self.adult_fio = adult_fio.title()
        self.document_number = self._prepare_document_number(document_number)
        self.event_type_code = self._event_type_code_to_obj(event_type_code, self.registry)
        self.effective_date = self._correct_date(effective_date)
        self.series_of_document = self._prepare_series_of_document(series_of_document)
        self.issuing_authority = self._prepare_issuing_authority(issuing_authority)
        self.document_date = self._correct_date(document_date)

    @property
    def get_data(self):
        return {
            'adult_snils': self.adult_snils,
            'adult_fio': self.adult_fio,
            'event_type_code': self.event_type_code,
            'effective_date': self.effective_date,
            'series_of_document': self.series_of_document,
            'document_number': self.document_number,
            'issuing_authority': self.issuing_authority,
            'document_date': self.document_date,
        }


class RegistryZpDTO(RegistryLrpDTO):
    """ Содержит данные полей реестра законных представителей. """

    registry = RegistryNameChoices.REGISTRY_ZP


class RegistryMsDTO(DTOBasic):
    """ Содержит данные полей реестра многодетных семей. """

    registry = RegistryNameChoices.REGISTRY_MS

    # Фамилия, Имя, Отчество главы семьи (заявителя);
    # СНИЛС главы семьи (заявителя);
    # Дата рождения главы семьи (заявителя);
    # Дата с;
    # Дата по;
    # Фамилия, Имя, Отчество ребенка;
    # Дата рождения ребенка

    def __init__(
            self,
            adult_snils: str,
            adult_fio: str,
            adult_date_of_birth: str,
            date_from: str,
            date_to: str,
            child_fio: str,
            child_date_of_birth: str,

    ):
        self.adult_snils = self._remowe_last_hyphen(adult_snils)
        self.adult_fio = adult_fio.title()
        self.adult_date_of_birth = self._reformat_data(adult_date_of_birth)
        self.date_from = self._reformat_data(date_from)
        self.date_to = self._reformat_data(date_to)
        self.child_fio = child_fio.title()
        self.child_date_of_birth = self._reformat_data(
            self._remove_end_of_line_chars(child_date_of_birth)
        )

    @property
    def get_data(self):
        return {
            'adult_snils': self.adult_snils,
            'adult_fio': self.adult_fio,
            'adult_date_of_birth': self.adult_date_of_birth,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'child_fio': self.child_fio,
            'child_date_of_birth': self.child_date_of_birth,
        }


class RegistryBrDTO(DTOBasic):
    """ Содержит данные полей реестра безработных граждан. """

    def __init__(
            self,
            last_name: str,
            first_name: str,
            patronymic: str,
            date_of_birth: str,
            snils: str,
            division: str,
            adress: str,
            phones: str,
            date_of_initial_appeal: str,
            date_registration_as_unemployed: str,
            payment_start_date: str,
            payment_end_date: str,
            name_of_the_payment: str,
            date_de_registration_as_unemployed: str,
            date_start_billing_period: str,
            date_end_billing_period: str,
            amount_accrued: str
    ):
        self.last_name = last_name.title()
        self.first_name = first_name.title()
        self.patronymic = patronymic.title()
        self.date_of_birth = self._reformat_data(date_of_birth, delimiter='/')
        self.snils = snils
        self.division = division
        self.adress = adress
        self.phones = phones
        self.date_of_initial_appeal = self._reformat_data(date_of_initial_appeal, delimiter='/')
        self.date_registration_as_unemployed = self._reformat_data(date_registration_as_unemployed, delimiter='/')
        self.payment_start_date = self._reformat_data(payment_start_date, delimiter='/')
        self.payment_end_date = self._reformat_data(payment_end_date, delimiter='/')
        self.name_of_the_payment = name_of_the_payment
        self.date_de_registration_as_unemployed = self._reformat_data(date_de_registration_as_unemployed, delimiter='/')
        self.date_start_billing_period = self._reformat_data(date_start_billing_period, delimiter='/')
        self.date_end_billing_period = self._reformat_data(date_end_billing_period, delimiter='/')
        self.amount_accrued = amount_accrued if amount_accrued else None

    @property
    def get_data(self):
        return {
            'fio': f'{self.last_name} {self.first_name} {self.patronymic}',
            'date_of_birth': self.date_of_birth,
            'snils': self.snils.replace('- ', '-'),
            'division': self.division,
            'adress': self.adress,
            'phones': self.phones,
            'date_of_initial_appeal': self.date_of_initial_appeal,
            'date_registration_as_unemployed': self.date_registration_as_unemployed,
            'payment_start_date': self.payment_start_date,
            'payment_end_date': self.payment_end_date,
            'name_of_the_payment': self.name_of_the_payment,
            'date_de_registration_as_unemployed': self.date_de_registration_as_unemployed,
            'date_start_billing_period': self.date_start_billing_period,
            'date_end_billing_period': self.date_end_billing_period,
            'amount_accrued': self.amount_accrued,
        }


class RegistryRtnTsDTO(DTOBasic):
    """ Содержит данные полей реестра Ростехнадзора по транспортным средствам. """

    def __init__(
            self,
            fio: str,
            date_of_birth: str,
            ts_name: str,
            ts_year_of_construct: str,
    ):
        self.fio = fio.title()
        self.date_of_birth = None if not date_of_birth else self._correct_date(date_of_birth)
        self.ts_name = ts_name.title()
        self.ts_year_of_construct = ts_year_of_construct

    @property
    def get_data(self):
        return {
            'fio': f'{self.fio}',
            'date_of_birth': self.date_of_birth,
            'ts_name': self.ts_name,
            'ts_year_of_construct': self.ts_year_of_construct,
        }


class RegistryLRPDopDTO(DTOBasic):
    def __init__(
            self,
            adult_fio: str,
            adult_passport_data: str,
            adult_registration_address: str,
            # Орган, выдавший документ
            issuing_authority: str,
            # Дата решения
            decision_date: str,
            # Номер и дата дела
            case_number_and_date: str,
            # Дата вступления решения в законную силу
            decision_entry_into_force_date: str,
            # Результат рассмотрения
            review_result: str,
            child_fio: str,
            child_birthday: str,
            # Наименование документа-основания
            name_foundation_document: str,
            # Реквизиты документа-основания
            details_foundation_document: str,
    ):
        self.adult_fio = adult_fio.strip()
        self.adult_passport_data = str(adult_passport_data).replace('г.р.', '').strip()
        self.adult_registration_address = str(adult_registration_address).strip()
        self.issuing_authority = issuing_authority.strip().strip()
        self.decision_date = self._reformat_data(str(decision_date).split(' ')[0], delimiter='/')
        self.case_number_and_date = str(case_number_and_date).strip()
        self.decision_entry_into_force_date = self._reformat_data(decision_entry_into_force_date, delimiter='/')
        self.review_result = str(review_result).strip()
        self.child_fio = str(child_fio).strip()
        self.child_birthday = self._reformat_data(str(child_birthday), delimiter='/')
        self.name_foundation_document = str(name_foundation_document).strip()
        self.details_foundation_document = str(details_foundation_document).strip()

    @property
    def get_data(self):
        return {
            'adult_fio': self.adult_fio,
            'adult_passport_data': self.adult_passport_data,
            'adult_registration_address': self.adult_registration_address,
            'issuing_authority': self.issuing_authority,
            'decision_date': self.decision_date,
            'case_number_and_date': self.case_number_and_date,
            'decision_entry_into_force_date': self.decision_entry_into_force_date,
            'review_result': self.review_result,
            'child_fio': self.child_fio,
            'child_birthday': self.child_birthday,
            'name_foundation_document': self.name_foundation_document,
            'details_foundation_document': self.details_foundation_document,
        }
