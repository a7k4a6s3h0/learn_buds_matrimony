from django.urls import path
from Home.urls import urlpatterns
from . import views

urlpatterns =[
    path('admin/home', views.admin_home, name="admin_home"),
    path('user/', views.usr_mng, name="user_management"),
    path('notification_management',views.NotifcationManagement.as_view(),name='notification_management'),
    path('admin/profile', views.admin_profile, name="admin_profille"),
]