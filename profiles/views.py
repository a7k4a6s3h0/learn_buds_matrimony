import django.contrib
from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
#profile display imports :
from django.shortcuts import render, get_object_or_404
from U_auth.models import *



class UserProfileView(TemplateView):
    template_name = 'users_pr_view.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id', None)
        if user_id:
            user = costume_user.objects.get(id=user_id)
            user_details = UserPersonalDetails.objects.get(user=user) 
            print(user_details.profile_pic.url)
            additional_details = AdditionalDetails.objects.get(user=user)
            pictures = Pictures.objects.filter(user=user_details)
            context['user_details'] = user_details
            context['additional_details'] = additional_details
            context['pictures'] = pictures
            return context

    




def messages_pg(request):
    return render(request, 'messages.html')


def user_send_pg(request):
    return render(request, 'send.html')


def user_accept_pg(request):
    return render(request, 'accept.html')


def user_reject_pg(request):
    return render(request, 'reject.html')


def user_recieved_pg(request):
    return render(request, 'recieved.html')

def user_chat_pg(request):
    return render(request, 'col_chat.html')


def user_shortlist_pg(request):
    return render(request, 'shortlist.html')

def user_shortlisted_pg(request):
    return render(request, 'shortlisted_by.html')

def user_contacted_pg(request):
    return render(request, 'contacted.html')

def user_viewed_pg(request):
    return render(request, 'pr_viewed.html')