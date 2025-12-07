from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User

# pylint: disable=too-few-public-methods
class CustomLoginForm(AuthenticationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username','email','password','confirm password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.order_fields(['username', 'email', 'password'])
        