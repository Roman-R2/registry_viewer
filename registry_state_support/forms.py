from django.forms import ModelForm

from mainapp.services import CheckSnils
from statisticapp.services import WorkWithStatistic


class StateSupportForm(ModelForm):
    class Meta:
        model = WorkWithStatistic.get_current_model_obj('registry_state_support')
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(StateSupportForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''

    def clean_adult_snils(self):
        field_name = 'adult_snils'
        snils = self.cleaned_data.get(field_name)
        if snils is not None and not CheckSnils(snils=snils).is_snils():
            error_message = 'Не являеися правильным СНИЛС'
            self.add_error(field_name, error_message)
        return snils

    def clean_child_snils(self):
        field_name = 'child_snils'
        snils = self.cleaned_data.get(field_name)
        if snils is not None and not CheckSnils(snils=snils).is_snils():
            error_message = 'Не являеися правильным СНИЛС'
            self.add_error(field_name, error_message)
        return snils

    def clean_another_adult_snils(self):
        field_name = 'another_adult_snils'
        snils = self.cleaned_data.get(field_name)
        if snils is not None and not CheckSnils(snils=snils).is_snils():
            error_message = 'Не являеися правильным СНИЛС'
            self.add_error(field_name, error_message)
        return snils
