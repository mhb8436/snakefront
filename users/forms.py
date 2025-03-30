from django import forms


class TokenForm(forms.Form):
    token = forms.CharField(label="Notebook token", max_length=100)
