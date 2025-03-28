from django import forms
from .models import User


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()


    class Meta:
        model = User
        fields = ['email', 'password']


class UserRegistrationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    password_check = forms.CharField()
    teacher_flag = forms.BooleanField()

    
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']


class ProfileChangeForm(forms.Form):
    new_first_name = forms.CharField()
    new_last_name = forms.CharField()
    new_password = forms.CharField()
    new_password_repeat = forms.CharField()
    gender = forms.CharField()