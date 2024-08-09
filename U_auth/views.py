from django.shortcuts import render

# Create your views here.

def demo(request):
    return render(request, 'base_files/base.html')

def login_view(request):
    return render(request, 'login.html')