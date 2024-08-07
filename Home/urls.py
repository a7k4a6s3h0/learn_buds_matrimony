from django.urls import path
from . import views


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('qualification', views.Qualification.as_view(), name='qualification'),
    path('loaction', views.Loaction.as_view(), name='loaction'),
    path('designation', views.Designation.as_view(), name='designation'),
]