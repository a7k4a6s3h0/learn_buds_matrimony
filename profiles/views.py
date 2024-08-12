from django.shortcuts import render
from U_auth.views import demo

# Create your views here.


def demo_pr(request):
    return render(request, 'otheruser_profile.html')


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