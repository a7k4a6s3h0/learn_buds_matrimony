from django.shortcuts import render
from django.views.generic import TemplateView

def admin_home(request):
    return render(request,"admin_home.html")

def usr_mng(request):
    return render(request,"user_manage.html")

class NotifcationManagement(TemplateView):
    template_name = "notification_management.html"