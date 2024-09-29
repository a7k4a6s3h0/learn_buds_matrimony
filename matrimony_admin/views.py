from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import AdminLoginForm
from U_auth.permissions import *
from U_auth.models import UserPersonalDetails, Location
from .forms import UserPersonalDetailsForm


class AdminHomeView(CheckSuperUserNotAuthendicated, TemplateView):
    template_name = "admin_home.html"

def usr_mng(request):
    users = UserPersonalDetails.objects.select_related('user', 'user_location')
    return render(request,"user_manage.html", {'users': users})

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


class NotifcationManagement(TemplateView):
    template_name = "notification_management.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['select_options'] = ['User 1', 'User 2', 'User 3']
        # Add other context variables if needed
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

