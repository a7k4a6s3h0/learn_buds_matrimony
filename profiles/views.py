from django.shortcuts import render

# Create your views here.


def demo_pr(request):
    return render(request, 'users_pr_view.html')


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