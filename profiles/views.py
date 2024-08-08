from django.shortcuts import render
from U_auth.views import demo

# Create your views here.


def demo_pr(request):
    return render(request, 'otheruser_profile.html')