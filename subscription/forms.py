# forms.py
from django import forms

class PaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
