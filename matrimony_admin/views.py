import json
import os
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView,DetailView,ListView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import AdminLoginForm, AdminProfileForm,NotificationDetailsForm
from .models import BlockedUserInfo
from U_auth.permissions import *

from U_auth.models import costume_user, UserPersonalDetails, Location
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDay
from subscription.models import Payment
from django.utils import timezone
from datetime import timedelta

from U_auth.models import *
from matrimony_admin.models import Subscription
from U_auth.permissions import *
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncDay
from datetime import datetime
from U_messages.models import NotificationDetails,AmidUsers
from .forms import UserPersonalDetailsForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class AdminHomeView(CheckSuperUserNotAuthendicated, TemplateView):
    template_name = "admin_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get today's date
        today = timezone.now().date()

        # 1. Data for the subscribers chart
        labels_subscribers = []
        data_subscribers = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            labels_subscribers.append(day.strftime("%b %d"))
            subscribers_count = Payment.objects.filter(created_at__date=day).count()
            data_subscribers.append(subscribers_count)

        # total subscribers
        total_subscribers = []
        subscribers_count = Payment.objects.filter(status="200").count()
        unsubscribers_count = Payment.objects.filter(status="unsub").count()
        total_subscribers = [subscribers_count, unsubscribers_count]

        # 3. Data for the income chart (Revenue per day for the current month)
        daily_revenue_data = (
            Payment.objects.filter(created_at__month=today.month)
            .annotate(day=TruncDay("created_at"))
            .values("day")
            .annotate(daily_income=Sum("amount"))
            .order_by("day")
        )

        # Prepare daily income data for the income chart
        days = [day for day in range(1, 32)]  # Days 1 to 31 of the month
        daily_income = {
            entry["day"].day: float(entry["daily_income"])
            for entry in daily_revenue_data
        }
        income_data = [
            daily_income.get(day, 0) for day in days
        ]  # Default income to 0 if no data for a day
        total_income = sum(income_data)  # total income till today

        # Get the current month and year
        now = timezone.now()
        first_day_of_month = now.replace(day=1)
        last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(
            day=1
        ) - timedelta(days=1)
        # Fetch users who joined this month
        new_users = costume_user.objects.filter(
            date_joined__gte=first_day_of_month, date_joined__lte=last_day_of_month
        )

        # Initialize arrays for arrivals and active users
        arrivals = [0] * 31  # Array for the days of the month (1-31)
        active_users = [0] * 31  # Array for the active users each day

        # Count new users per day
        for user in new_users:
            arrivals[user.date_joined.day - 1] += 1

        for day in range(1, 31):
            # Fetch the count of active users for the given day
            active_users[day - 1] = costume_user.objects.filter(
                last_login__date=now.replace(day=day).date()
            ).count()

        # Add data to context
        context["label"] = list(range(1, 32))  # Days of the month
        context["arrivals"] = arrivals
        context["active_users"] = active_users

        current_active = costume_user.objects.filter(
            last_login__date=now.date()
        ).count()
        total_users = costume_user.objects.count()
        blocked_users = BlockedUserInfo.objects.select_related(
            "user", "user__user_details"
        ).all()

        # Aggregate the total revenue for payments with status 200
        matrimony_revenue = Payment.objects.filter(status=200).aggregate(
            total_revenue=Sum("amount")
        )["total_revenue"]

        context["matrimony_revenue"] = matrimony_revenue
        context["current_active"] = current_active
        context["total_users"] = total_users
        context["subscribers_count"] = subscribers_count
        context["total_income"] = total_income
        context["income_data"] = income_data
        context["labels_subscribers"] = labels_subscribers
        context["data_subscribers"] = data_subscribers
        context["total_subscribers"] = total_subscribers
        context["blocked_users"] = blocked_users

        return context


class UserManagementView(ListView):
    model = UserPersonalDetails
    template_name = 'user_manage.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        # Use select_related to optimize query and reduce DB hits
        return UserPersonalDetails.objects.select_related('user', 'user_location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Get the pagination object and handle the page request
            page_number = self.request.GET.get('page')
            paginator = Paginator(self.get_queryset(), self.paginate_by)
            page_obj = paginator.get_page(page_number)
            context['page_obj'] = page_obj
        except (PageNotAnInteger, EmptyPage):
            # If page is not an integer, deliver first page.
            # If page is out of range, deliver last page of results.
            context['page_obj'] = paginator.page(1 if isinstance(PageNotAnInteger) else paginator.num_pages)
        except Exception as e:
            # Handle unexpected exceptions (optional)
            context['error_message'] = f"An error occurred: {str(e)}"
        
        return context

  
@method_decorator(csrf_exempt, name='dispatch')
class BlockUnblockUserView(View):
    
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('userId')
        is_active = request.POST.get('isActive') == "true"  # Ensure proper boolean conversion
        block_reason = request.POST.get('blockReason', '')

        try:
            user_details = costume_user.objects.get(id=user_id)
            user = user_details.user  # Get the related User instance
            
            # Update the user's active status
            user.is_active = is_active
            # user_details.is_blocked = not is_active  # Reflect if the user is blocked or not

            # If the user is blocked, store the block reason
            if not is_active:
                user_details.block_reason = block_reason
            else:
                user_details.block_reason = None  # Clear the block reason when unblocked

            user.save()  # Save the related User model
            user_details.save()  # Save the UserPersonalDetails model

            print(f"User {user_id} block status: {user_details.is_blocked}, reason: {user_details.block_reason}")


            return JsonResponse({'status': 'success'})

        except UserPersonalDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


class AdminLoginView(CheckSuperUserAuthendicated, FormView):
    template_name = "admin_login.html"
    form_class = AdminLoginForm
    success_url = reverse_lazy("admin_home")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        user = authenticate(email=email, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            messages.error(self.request, "Invalid credentials")
            return self.form_invalid(form)


class AdminLogoutView(CheckSuperUserNotAuthendicated, TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("admin_login")


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


class admin_profile(CheckSuperUserNotAuthendicated, FormView):
    template_name = "admin_profile.html"
    form_class = AdminProfileForm
    
    
class SubscriptionManagementView(ListView):
    model = Subscription
    template_name = 'admin_subscription.html' 
    context_object_name = 'subscriptions'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    

#arjun

from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from .models import Add_expense
from .forms import AddExpenseForm  # Assuming you have a form for your model

class AddExpenseView(CreateView):
    model = Add_expense
    form_class = AddExpenseForm  # Use the form you created for AddExpense
    template_name = 'add_expense.html'  # Your template for adding expenses
    success_url = reverse_lazy('add_expense')  # Redirect after successful submission

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expenses'] = Add_expense.objects.all()  # Fetch all expenses for display
        return context
def add_user(request):
    if request.method == 'POST':
        form = UserPersonalDetailsForm(request.Post, request.Files)
        if form.is_valid():
            form.save()
            messages.success(request, 'User added successfully!')
            return redirect('usr_mng')
        else:
            form = UserPersonalDetailsForm()
        return render(request, 'matrimony_admin/user_management.html', {'form': form})

def edit_user(request, pk):
    user_details = get_object_or_404(UserPersonalDetails, pk=pk)
    if request.method == 'POST':
        form = UserPersonalDeatilsForm(request.POST, request.FILES, instance=user_details)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('usr_mng')
    else:
        form = UserPersonalDetailsForm(instance=user_details)
    return render(request, 'matrimony_admin/user_management.html', {'form': form, 'user': user_details})
