from django.urls import path
from Home.urls import urlpatterns
from . import views

urlpatterns = [
    path('admin_login', views.AdminLoginView.as_view(), name='admin_login'),
    path('admin_logout', views.AdminLogoutView.as_view(), name='admin_logout'),
    path('admin_home', views.AdminHomeView.as_view(), name="admin_home"),
    path('financial_management',views.FinancialManagement.as_view(), name='financial_management'),
    path('user/', views.UserManagementView.as_view(), name="user_management"),
    path('edit_user/<int:pk>/', views.EditUserView.as_view(), name='edit_user'),
    
    path('block-unblock-user/', views.BlockUnblockUserView.as_view(), name='block_unblock_user'),
    path('delete-users/', views.DeleteUserView.as_view(), name='delete_users'),
    path('notification_management',views.NotifcationManagement.as_view(),name='notification_management'),
    path('subscription_management',views.SubscriptionManagementView.as_view(),name='subscription_management'),
    path('user/add/', views.add_user, name='add_user'),
    path('user/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('block-unblock-user/', views.BlockUnblockUserView.as_view(), name='block_unblock_user'),
    path('add-expense/', views.AddExpenseView.as_view(), name='add_expense'),#arjun
]