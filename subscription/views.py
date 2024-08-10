from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class AddPaymentView(TemplateView):
    template_name='AddPayment.html'
    
class SubscriptionView(TemplateView):
    template_name='Subscription.html'
    
class AddCardView(TemplateView):
    template_name='Addcard.html'