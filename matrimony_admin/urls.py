from django.urls import path
from Home.urls import urlpatterns
from . import views

urlpatterns =[
    path('admin/home', views.admin_home, name="admin_home")
]