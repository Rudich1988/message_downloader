from django import forms
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from apps.users.models import CustomUser


USERNAME_HELP_TEXT = ('Обязательное поле. Не более 150 символов. '
                      'Только буквы, цифры и символы @/./+/-/_.')
PASSWORD_ERROR_TEXT = ('Введённый пароль слишком короткий. '
                       'Он должен содержать как минимум 3 символа.')
PASSWORD_HELP_TEXT = 'Ваш пароль должен содержать как минимум 3 символа.'
PASSWORD2_HELP_TEXT = 'Для подтверждения введите, пожалуйста, пароль ещё раз.'


class UserRegistrationForm(UserCreationForm):

    first_name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилия')
    username = forms.CharField(label='Имя пользователя',
                               help_text=USERNAME_HELP_TEXT)
    password1 = forms.CharField(label='Пароль',
                                help_text=PASSWORD_HELP_TEXT,
                                widget=forms.PasswordInput())
    password2 = forms.CharField(label='Подтверждение пароля',
                                help_text=PASSWORD2_HELP_TEXT,
                                widget=forms.PasswordInput(),
                                validators=[MinLengthValidator(3,
                                                               message=
                                                               PASSWORD_ERROR_TEXT)])

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя',
                               widget=forms.TextInput())
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = ('username', 'password')
