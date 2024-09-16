from django.urls import path
from . import views


urlpatterns = [
    path('subscribe',views.SubscriptionView.as_view(),name='subscribe'),
    path('addpayment',views.AddPaymentView.as_view(),name='addpayment'),
    
    path('pay/', views.PaymentView.as_view(), name='payment'),
    path('payment-callback/', views.PaymentCallbackView.as_view(), name='payment-callback'),
    path('payment-success/',views.PaymentSuccess.as_view(), name='payment-success'),
    path('invoice/',views.Invoice.as_view(), name='invoice'),
]