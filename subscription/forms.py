# forms.py
from django import forms

class PaymentForm(forms.Form):
    plan_type = forms.CharField(max_length=100)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
