from django.contrib.auth.forms import (AuthenticationForm, UserChangeForm,
                                       UserCreationForm)
from django.forms.widgets import TextInput

from authapp.models import AppExtendedUser


class AppExtendedUserLoginForm(AuthenticationForm):
    class Meta:
        model = AppExtendedUser
        fields = ('username', 'password',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class AppExtendedUserRegisterForm(UserCreationForm):
    class Meta:
        model = AppExtendedUser
        fields = (
            'last_name',
            'first_name',
            'patronymic',
            'username',
            'office',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs.update(
            {
                'autofocus': 'false'
            }
        )
        self.fields['last_name'].widget.attrs.update(
            {
                'autofocus': 'autofocus',
                'required': 'required',
                'placeholder': 'Фамилия'
            }
        )
        self.fields['first_name'].widget.attrs.update(
            {
                'required': 'required',
                'placeholder': 'Имя'
            }
        )
        self.fields['patronymic'].widget.attrs.update(
            {
                'required': 'required',
                'placeholder': 'Отчество'
            }
        )

    # def clean_age(self):
    #     data_age = self.cleaned_data['age']
    #     if data_age < 18:
    #         raise forms.ValidationError('Вам мало лет.')
    #     return data_age
