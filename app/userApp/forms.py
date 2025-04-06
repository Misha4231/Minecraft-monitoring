from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("email",)

class NewUserForm(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['email','captcha']

class LoginForm(forms.Form):
    username = forms.EmailField()
    password = forms.CharField()