from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import AdminLoginForm,AdminProfileForm
from U_auth.permissions import *



class AdminHomeView(CheckSuperUserNotAuthendicated, TemplateView):
    template_name = "admin_home.html"

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


class NotifcationManagement(TemplateView):
    template_name = "notification_management.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['select_options'] = ['User 1', 'User 2', 'User 3']
        # Add other context variables if needed
        return context
    

# def admin_profile(request):
#     return render(request,"admin_profile.html")


class admin_profile(CheckSuperUserNotAuthendicated,FormView):
    template_name = "admin_profile.html"
    form_class = AdminProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin_details'] = self.request.user
        return context
    