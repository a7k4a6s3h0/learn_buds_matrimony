# views.py
import django.contrib
from typing import Any
from urllib import request

from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import redirect, render
import razorpay
from django.conf import settings
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from .forms import PaymentForm
from django.contrib import messages
from .models import Payment
from django.urls import reverse

from matrimony_admin.models import Subscription, SubscriptionINFO

from U_auth.permissions import RedirectNotAuthenticatedUserMixin
from http import HTTPStatus

class PaymentView(RedirectNotAuthenticatedUserMixin,FormView):
    template_name = 'Addcard.html'
    form_class = PaymentForm
    success_url = reverse_lazy('payment-success')

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
 
        plan = request.GET.get('plan_type', None)
        print(plan, "plan...............>>!!!!!!!!!!!!!!")
        
        # Store the selected plan in session
        if not request.session.get('plan_type'):
            request.session['plan_type'] = plan
        
        if plan:
            context = {
                'status': HTTPStatus.OK,
                'redirect': True,
                'redirect_url': 'pay'
            }
            return JsonResponse(context)
        
        try:
            # Get the plan from session if it exists
            session_plan = request.session.get('plan_type', None)
            print(session_plan,"ooooooooooooooooooooooooo")
            subscription = Subscription.objects.get(plan_type=session_plan)
            
            context = {
                'plan': subscription.plan_type,
                'amount': subscription.price
            }
            return self.render_to_response(context)
        
        except Subscription.DoesNotExist:
            # If subscription does not exist, show an error and redirect
            messages.error(request, "Choose a Plan...!!!")
            return redirect(reverse('subscribe'))  # Redirects to the subscription page
        

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

        print(razorpay_order,"order details")

        # Save the order details in the database
        payment = Payment.objects.create(
            user = self.request.user,
            payment_type = 'razorpay',
            subscription_plan = Subscription.objects.get(plan_type=self.request.session.pop('plan_type')),
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
    template_name = 'Addcard.html'
    
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

        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)

        try:
            # Signature verification
            client.utility.verify_payment_signature(params_dict)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = HTTPStatus.OK
            payment.save()
            context = {'status': 'Payment Successful'}
        except:
            payment.status = HTTPStatus.BAD_REQUEST
            payment.save()
            context = {'status': 'Payment Failed'}

        print(context,"in PaymentCallbackView post method")
        return self.render_to_response(context)
        # return reverse('')
    
class PaymentSuccess(RedirectNotAuthenticatedUserMixin,TemplateView):
    template_name='payment_success.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs) 
        print("in context")
        context["payment_details"] = Payment.objects.filter(user=self.request.user)
        print(Payment.objects.filter(user=self.request.user))
        # print(context)
        return context
    

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)
    
class SubscriptionView(TemplateView):
    template_name='Subscribe.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        subscription_details = Subscription.objects.all()
        context['subscription_details'] = subscription_details

        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        previous_url = request.META.get('HTTP_REFERER', '/default-url/')
        # next_url = request.GET.get('next', '/default-url/')  # If 'next' not provided, use default
        print(previous_url, "url.....")
        return super().get(request, *args, **kwargs)
    
class AddPaymentView(TemplateView):
    template_name='AddPayment.html'


class Invoice(TemplateView):
    template_name='sample-invoice-converted.html'
    