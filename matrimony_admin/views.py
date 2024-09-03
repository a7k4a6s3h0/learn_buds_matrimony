from django.shortcuts import render

def admin_home(request):
    return render(request,"admin_home.html")

def usr_mng(request):
    return render(request,"user_manage.html")
