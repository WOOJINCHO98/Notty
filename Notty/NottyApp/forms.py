from django import forms
from .models import Route
from .models import Account


class RouteForm(forms.Form):
    start = forms.CharField(max_length=30)
    fin = forms.CharField(max_length=30)

class Account(forms.Form):
    class Meta:
        model = Account
        field = '__all__'
