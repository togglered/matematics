from django import forms


class NewTestName(forms.Form):
    new_name = forms.CharField()