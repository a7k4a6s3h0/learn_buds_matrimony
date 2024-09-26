from django.shortcuts import render
from django.views.generic import TemplateView

def admin_home(request):
    return render(request,"admin_home.html")

def usr_mng(request):
    return render(request,"user_manage.html")

class NotifcationManagement(TemplateView):
    template_name = "notification_management.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['select_options'] = ['User 1', 'User 2', 'User 3']
        # Add other context variables if needed
        return context
    

def admin_profile(request):
    return render(request,"admin_profile.html")
