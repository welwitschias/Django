from django.contrib.auth.forms import UserCreationForm, User
from django import forms


class UserForm(UserCreationForm):
    email = forms.EmailField(label="이메일")

    class Meta:
        model = User
        fields = ("username", "email")
