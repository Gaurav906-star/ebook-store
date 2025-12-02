from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User


class CustomLoginForm(AuthenticationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username','email','password','confirm password']