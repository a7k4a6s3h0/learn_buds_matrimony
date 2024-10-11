from django.urls import path
from Home.urls import urlpatterns
from . import views

urlpatterns =[
    path('admin_login', views.AdminLoginView.as_view(), name='admin_login'),
    path('admin_logout', views.AdminLogoutView.as_view(), name='admin_logout'),
    path('admin_home', views.AdminHomeView.as_view(), name="admin_home"),
    path('financial_management',views.FinancialManagement.as_view(), name='financial_management'),
    path('user/', views.UserManagementView.as_view(), name="user_management"),
    path('blkunblk/',views.BlockUnblockUserView.as_view(), name="BlockUnblock"),
    path('notification_management',views.NotifcationManagement.as_view(),name='notification_management'),
    path('subscription_management',views.SubscriptionManagementView.as_view(),name='subscription_management'),
    path('admin_profile', views.admin_profile.as_view(), name="admin_profile"),
    path('add-expense/', views.AddExpenseView.as_view(), name='add_expense'),#arjun
]