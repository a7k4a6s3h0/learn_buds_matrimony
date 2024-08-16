from django.urls import path
from . import views


urlpatterns = [
    path('subscribe',views.SubscriptionView.as_view(),name='subscribe'),
    path('addpayment',views.AddPaymentView.as_view(),name='addpayment'),
    path('addcard',views.AddCardView.as_view(),name='addcard'),
    path('demo',views.DemoView.as_view(),name='demo'),
]