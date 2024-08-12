from django.shortcuts import render

# Create your views here.

def AuthPage(request):
    context = {
        'experance_level': ['Beginner', 'Intermediate', 'Expert'],
        'marital_status': ['Unmarried', 'Divorced']
    }
    return render(request, 'auth/auth.html',context)
