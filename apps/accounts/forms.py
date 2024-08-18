from django import forms

from apps.accounts.models import UserEmailAccount


class AccountCreateForm(forms.ModelForm):

    email = forms.CharField(label='Имя аккаунта')
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput())

    class Meta:
        model = UserEmailAccount
        fields = ['email', 'password']
