from django.urls import path
from Home.urls import urlpatterns
from . import views

urlpatterns =[
    path('home', views.admin_home, name="home"),
    path('user/', views.usr_mng, name="user_management"),
    path('notification_management',views.NotifcationManagement.as_view(),name='notification_management')
]