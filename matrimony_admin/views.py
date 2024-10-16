import json
import os
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView,DeleteView,UpdateView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import FormView, ListView
from django.urls import reverse_lazy
from .forms import AdminLoginForm, AdminProfileForm,NotificationDetailsForm, EditUserForm
from .models import BlockedUserInfo
from U_auth.permissions import *
from U_auth.models import UserPersonalDetails, Location
from .forms import UserPersonalDetailsForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from U_auth.models import costume_user
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDay
from subscription.models import Payment
from django.utils import timezone
from datetime import timedelta

from U_auth.models import *
from matrimony_admin.models import Subscription
from U_auth.permissions import *
from django.db.models import Count, Sum, F, Case, When, DecimalField
from django.db.models.functions import TruncMonth, TruncDay
from datetime import datetime
from U_messages.models import NotificationDetails, AmidUsers


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
        daily_financial_data = (
            Add_expense.objects.filter(date__month=today.month, date__lte=today)
            .annotate(day=TruncDay("date"))
            .values("day")
            .annotate(
                daily_income=Sum(
                    Case(
                        When(cr__gt=F("dr"), then=F("cr") - F("dr")),
                        default=0,
                        output_field=DecimalField(),
                    )
                ),
                daily_expense=Sum(
                    Case(
                        When(dr__gt=F("cr"), then=F("dr") - F("cr")),
                        default=0,
                        output_field=DecimalField(),
                    )
                ),
            )
            .order_by("day")
        )

        # Prepare daily income and expense data for the chart
        days = [
            day for day in range(1, today.day + 1)
        ]  # Days 1 to current day of the month
        daily_income = {
            entry["day"].day: float(entry["daily_income"] or 0)
            for entry in daily_financial_data
        }
        daily_expense = {
            entry["day"].day: float(entry["daily_expense"] or 0)
            for entry in daily_financial_data
        }

        income_data = [daily_income.get(day, 0) for day in days]
        expense_data = [daily_expense.get(day, 0) for day in days]

        total_income = sum(income_data)
        total_expense = sum(expense_data)
        profit = total_income - total_expense

        # Add financial data to context
        context["labels"] = days
        context["income_data"] = income_data
        context["expense_data"] = expense_data
        context["total_income"] = total_income
        context["total_expense"] = total_expense
        context["profit"] = profit

        # customer arrivals
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
        
        return UserPersonalDetails.objects.select_related('user', 'user_location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Retrieve payment details for each user and assign subscription status
        user_subscriptions = {}
        for user in context['users']:
            # Fetch the latest payment for each user, if any
            payment = user.user.userpayment_details.order_by('-created_at').first()
            if payment:
                user.subscription_type = payment.status  # Store payment status as subscription type
            else:
                user.subscription_type = 'No Subscription'
            user_subscriptions[user.id] = user.subscription_type

        context['user_subscriptions'] = user_subscriptions

        return context

class DeleteUserView(View):
    success_url = reverse_lazy('user_manage')  # Redirect after successful deletion

    def post(self, request, *args, **kwargs):
        # Get the list of selected users from POST data
        selected_users = request.POST.getlist('selected_users')

        if selected_users:
            # Delete all selected users
            costume_user.objects.filter(id__in=selected_users).delete()

        return HttpResponseRedirect(self.success_url)
        
@method_decorator(csrf_exempt, name='dispatch')
class BlockUnblockUserView(View):

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('userId')
        is_active = request.POST.get('isActive') == "true"  # "true" for unblock, "false" for block
        block_reason = request.POST.get('blockReason', '')  # Reason for blocking (if applicable)

        try:
            # Get the user instance (UserPersonalDetails model)
            user_details = UserPersonalDetails.objects.get(id=user_id)


            # Update the user's active status
            user_details.user.is_active = is_active
            user_details.user.save()  # Save the updated status of the user

            if not is_active:
                # Block user: Update UserPersonalDetails
                user_details.is_blocked = True
                user_details.block_reason = block_reason  # Set block reason
            else:
                # Unblock user: Clear block details
                user_details.is_blocked = False
                user_details.block_reason = None  # Clear the block reason
            
            user_details.save()  # Save the updated UserPersonalDetails

            # Handle BlockedUserInfo for tracking blocks
            if not is_active:
                # Store or update BlockedUserInfo
                blocked_user_info, created = BlockedUserInfo.objects.get_or_create(user=user_details.user)
                blocked_user_info.reason = block_reason  # Set or update block reason
                blocked_user_info.times += 1  # Increment block count
                blocked_user_info.save()  # Save the BlockedUserInfo entry
            else:
                # Unblock user: Remove BlockedUserInfo if exists
                BlockedUserInfo.objects.filter(user=user_details.user).delete()

            return JsonResponse({'status': 'success', 'is_active': is_active})

        except UserPersonalDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



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
    success_url = "notification_management"

    def post(self, request: HttpRequest, *args: str, **kwargs: dict) -> HttpResponse:
        form = self.form_class(request.POST)
        if form.is_valid():
            notification = form.save(commit=True)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context = ['users'] = costume_user.objects.all()
        context["select_options"] = ["User 1", "User 2", "User 3"]
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
    template_name = "admin_subscription.html"
    context_object_name = "subscriptions"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# arjun

from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from .models import Add_expense
from .forms import AddExpenseForm  # Assuming you have a form for your model


class AddExpenseView(CreateView):
    model = Add_expense
    form_class = AddExpenseForm  # Use the form you created for AddExpense
    template_name = "add_expense.html"  # Your template for adding expenses
    success_url = reverse_lazy("add_expense")  # Redirect after successful submission

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["expenses"] = (
            Add_expense.objects.all()
        )  # Fetch all expenses for display
        return context


class EditUserView(UpdateView):
    model = UserPersonalDetails
    form_class = EditUserForm

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(UserPersonalDetails, pk=user_id)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            self.form_valid(form)
            return redirect('user_management')  # Redirect to user management page after success
        else:
            self.form_invalid(form)
            return self.render_to_response({'form': form})

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the user.')
        return super().form_invalid(form)