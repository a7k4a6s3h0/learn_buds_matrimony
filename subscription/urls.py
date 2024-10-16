from django.urls import path
from .import views


urlpatterns = [
    path('subscribe',views.SubscriptionView.as_view(),name='subscribe'),
    path('addpayment',views.AddPaymentView.as_view(),name='addpayment'),
    
    path('pay/', views.PaymentView.as_view(), name='payment'),
    path('payment-callback/', views.PaymentCallbackView.as_view(), name='payment-callback'),
    # For viewing payment details (without pay_id)
    path('payment-details/', views.PaymentDetails.as_view(), name='payment-details'),

    # For downloading a specific invoice (with pay_id)
    path('payment-details/<int:pay_id>/', views.PaymentDetails.as_view(), name='payment-datas'),
    path('invoice/',views.Invoice.as_view(), name='invoice'),
]