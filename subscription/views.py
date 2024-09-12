# views.py
from typing import Any
from urllib import request
import razorpay
from django.conf import settings
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from .forms import PaymentForm
from .models import Payment
from django.http import JsonResponse
from U_auth.permissions import RedirectNotAuthenticatedUserMixin

class PaymentView(RedirectNotAuthenticatedUserMixin,FormView):
    template_name = 'Addcard.html'
    form_class = PaymentForm
    success_url = reverse_lazy('payment-success')

    def form_valid(self, form):
        # Get the amount entered by the user
        amount = int(form.cleaned_data['amount'] * 100)  # Convert to paise

        # Create Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create an order
        razorpay_order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Save the order details in the database
        payment = Payment.objects.create(
            user = self.request.user,
            razorpay_order_id=razorpay_order['id'],
            amount=form.cleaned_data['amount'],
            status='created'
        )
        
        # Pass the payment details to the template
        context = {
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'amount': amount,
            'currency': 'INR',
            'callback_url': self.request.build_absolute_uri(reverse_lazy('payment-callback'))
        }
        print(context)
        return JsonResponse(context)
    
class PaymentCallbackView(RedirectNotAuthenticatedUserMixin,TemplateView):
    template_name = 'payment_status.html'
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs) 
        
        context["payment_details"] = Payment.objects.get(user=self.request.user)
        # print(context)
        return context
    

    def post(self, request, *args, **kwargs):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Razorpay payment details from request
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')

        # Verify the payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            # Signature verification
            client.utility.verify_payment_signature(params_dict)
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'successful'
            payment.save()
            context = {'status': 'Payment Successful'}
        except:
            context = {'status': 'Payment Failed'}

        return self.render_to_response(context)
    
class PaymentSuccess(TemplateView):
    template_name='payment_success.html'
    
class SubscriptionView(TemplateView):
    template_name='Subscribe.html'
    
class AddPaymentView(TemplateView):
    template_name='AddPayment.html'
    