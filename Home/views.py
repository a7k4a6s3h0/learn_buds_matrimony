from django.shortcuts import render
from django.views.generic import TemplateView
from U_auth.permissions import RedirectAuthenticatedUserMixin, RedirectNotAuthenticatedUserMixin
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
# Create your views here.
class Home(RedirectNotAuthenticatedUserMixin, TemplateView):
    template_name='Home/home.html'


class Qualification(TemplateView):
    template_name='Home/qualification.html'

class Loaction(TemplateView):
    template_name='Home/loaction.html'


class Designation(TemplateView):
    template_name='Home/designation.html'


class FilterPrifles(TemplateView):
    template_name='Home/filter.html'

# class error404(TemplateView):
#     template_name='Home/error.html'    

    