from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class SubscriptionView(TemplateView):
    template_name='Subscribe.html'
    
class AddPaymentView(TemplateView):
    template_name='AddPayment.html'
     
class AddCardView(TemplateView):
    template_name='Addcard.html'
    
class DemoView(TemplateView):
    template_name='demo.html'
    