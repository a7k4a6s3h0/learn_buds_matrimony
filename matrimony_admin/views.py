import json
import os
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import AdminLoginForm,AdminProfileForm,NotificationDetailsForm
from .models import *
from subscription.models import Payment
from U_auth.models import *
from U_auth.permissions import *
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncDay
from datetime import datetime
from U_messages.models import NotificationDetails,AmidUsers

class AdminHomeView(CheckSuperUserNotAuthendicated, TemplateView):
    template_name = "admin_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Aggregate payments by month and count number of subscribers
        monthly_subscriber_data = Payment.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(subscriber_count=Count('id')).order_by('month')

        # Prepare data for chart: List of month names and counts
        months = [entry['month'].strftime('%B') for entry in monthly_subscriber_data]
        monthly_subscriber_counts = [entry['subscriber_count'] for entry in monthly_subscriber_data]

        #Debigging
        print(months,"months")
        print(monthly_subscriber_counts,'monthly_subscriber_counts')

        # Add to context for use in the template
        context['months'] = months  # List of month names
        context['monthly_subscriber_counts'] = monthly_subscriber_data  # List of counts

        # Aggregate payments by day and count the number of subscribed and unsubscribed users
        daily_subscriber_data = Payment.objects.annotate(day=TruncDay('created_at')).values('day').annotate(
            subscribed_count=Count('id', filter=Q(status='subscribed')),
            unsubscribed_count=Count('id', filter=Q(status='unsubscribed'))
        ).order_by('day')

        # Prepare data for chart: List of day names and subscriber/unsubscriber counts
        daily = [entry['day'].strftime('%d %B') for entry in daily_subscriber_data]  # Format as '01 January'
        subscribed_counts = [entry['subscribed_count'] for entry in daily_subscriber_data]
        unsubscribed_counts = [entry['unsubscribed_count'] for entry in daily_subscriber_data]

        # Add to context for use in the template
        context['daily'] = daily  # List of day names
        context['subscribed_counts'] = subscribed_counts  # List of subscribed counts
        context['unsubscribed_counts'] = unsubscribed_counts  # List of unsubscribed counts

        #Debigging
        print(daily,"daily")
        print(subscribed_counts,'daily_subscriber_counts')
        print(unsubscribed_counts,'unsubscribed_counts')

        # Aggregate the total revenue for payments with status 200
        matrimony_revenue = Payment.objects.filter(status=200).aggregate(total_revenue=Sum('amount'))['total_revenue']
        context['matrimony_revenue'] = matrimony_revenue

        #Debugging
        print(matrimony_revenue,'matrimony_revenue')
        
        # Aggregate active and total users per day, including today's new users
        customer_data = costume_user.objects.annotate(day=TruncDay('date_joined')).values('day').annotate(
            new_users=Count('id'),  # Count of users who joined each day
            active_user_count=Count('id', filter=Q(is_active=True)),  # Count of active users
            total_users=Count('id')  # Total users (up to the current day)
        ).order_by('day')

        
        # result = self.read_or_write_json('users_details.json', customer_data)
        # if result:
        #     print(result,"datas...........!!!!")


        # Convert day to digit format for display (e.g., '01', '02', etc.)
        day_in_digit = [entry['day'].strftime('%d') for entry in customer_data]

        # Output can be added to the context for a template or further processing
        context['customer_data'] = customer_data
        context['day_in_digit'] = day_in_digit

        # Debugging
        # customer_data output example
        '''<QuerySet [{'day': datetime.datetime(2024, 9, 27, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')), 
        'new_users': 1, 'active_user_count': 1, 'total_users': 1}]> customer_data'''
        
        print(customer_data,  'customer_data')
        print(day_in_digit, 'day_in_digit')

        return context
    

    # def read_or_write_json(self, file_path, default_content):
    #     # Check if the file exists and is non-empty
    #     if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
    #         # If file exists and has content, read the JSON data
    #         with open(file_path, 'r') as json_file:
    #             try:
    #                 data = json.load(json_file)
    #                 print("Data loaded successfully:", data)
    #                 # Assuming default_content is today's data and data is yesterday's data
    #                 percentage_change = self.calculate_percentage_change(default_content, data)
                    
    #                 # After calculating, update the file with today's data
    #                 self.write_today_data(file_path, default_content)
    #                 return percentage_change  # Return the calculated percentage change
                    
    #             except json.JSONDecodeError:
    #                 print("Error reading JSON file.")
    #                 return None
    #     else:
    #         # If the file does not exist or is empty, write the default content (today's data)
    #         self.write_today_data(file_path, default_content)
    #         return default_content  # Return the default content

    # # Separate function to handle writing today's data
    # def write_today_data(self, file_path, today_data):
    #     with open(file_path, 'w') as json_file:
    #         json.dump(today_data, json_file, indent=4)
    #         print(f"Today's content written to {file_path}.")

    # # Calculate percentage change (e.g., today's vs. yesterday's data)
    # def calculate_percentage_change(self, today_data, yesterday_data):
    #     # Assuming you're comparing specific numerical values
    #     if yesterday_data == 0:
    #         return 0  # Avoid division by zero
    #     return ((today_data - yesterday_data) / yesterday_data) * 100


def usr_mng(request):
    return render(request,"user_manage.html")

class AdminLoginView(CheckSuperUserAuthendicated ,FormView):
    template_name = 'admin_login.html'
    form_class = AdminLoginForm
    success_url = reverse_lazy('admin_home')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        user = authenticate(email=email, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid credentials')
            return self.form_invalid(form)
    
class AdminLogoutView(CheckSuperUserNotAuthendicated ,TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('admin_login')

class FinancialManagement(TemplateView):
    template_name = "financial_management.html"


class NotifcationManagement(FormView):
    template_name = "notification_management.html"
    form_class = NotificationDetailsForm
    success_url = 'notification_management'


    def post(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:
        form = self.form_class(request.POST)
        if form.is_valid():
            notification = form.save(commit=True)
        return super().post(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context = ['users'] = costume_user.objects.all()
        context['select_options'] = ['User 1', 'User 2', 'User 3']
        # Add other context variables if needed
        return context
    # def get_success_url(self) -> str:
    #     return reverse_lazy('notification_management')
    


# def admin_profile(request):
#     return render(request,"admin_profile.html")


class admin_profile(CheckSuperUserNotAuthendicated,FormView):
    template_name = "admin_profile.html"
    form_class = AdminProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin_details'] = self.request.user
        return context
    