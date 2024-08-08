from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
class Home(TemplateView):
    template_name='Home/home.html'


class Qualification(TemplateView):
    template_name='Home/qualification.html'

class Loaction(TemplateView):
    template_name='Home/loaction.html'


class Designation(TemplateView):
    template_name='Home/designation.html'