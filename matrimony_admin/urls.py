from django.urls import path
from Home.urls import urlpatterns
from . import views

urlpatterns =[
    path('admin_login', views.AdminLoginView.as_view(), name='admin_login'),
    path('admin_logout', views.AdminLogoutView.as_view(), name='admin_logout'),
    path('admin_home', views.AdminHomeView.as_view(), name="admin_home"),
    path('financial_management',views.FinancialManagement.as_view(), name='financial_management'),
    path('home', views.admin_home, name="home"),
    path('user/', views.usr_mng, name="user_management"),
    path('notification_management',views.NotifcationManagement.as_view(),name='notification_management')
]