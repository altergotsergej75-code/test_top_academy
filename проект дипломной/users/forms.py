from django import forms
from django.contrib.auth.models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Пароль"
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Подтвердите пароль"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password")

        labels = {
            "username": "Имя пользователя",
            "email": "Email",
        }

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают.")

        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Имя пользователя"
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Пароль"
    )