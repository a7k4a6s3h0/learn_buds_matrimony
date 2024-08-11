from django.shortcuts import render

# Create your views here.

def demo(request):
    return render(request, 'base_files/base.html')

def login_view(request):
    return render(request, 'login.html')
def perdet_view(request):
    return render(request, 'personal details.html')
def jobst(request):
    return render(request, 'job status.html')
def jobd(request):
    return render(request, 'Job Details.html')
def jobd1(request):
    return render(request, 'Job Details2.html')
def relation(request):
    return render(request, 'Relationship.html')
def interest(request):
    return render(request, 'Interested.html')
def adddet(request):
    return render(request, 'Additional details.html')