from django.urls import path
from . import views


urlpatterns = [

    path('user_pr/', views.user_details, name="user_pr"),
    path('user_pr_2/', views.user_details_2, name="user_pr_2"),
    path('user_pr_3/', views.user_details_3, name="user_pr_3"),
    path('user_pr_4/', views.user_details_4, name="user_pr_4"),
    path('user_pr_5/', views.user_details_5, name="user_pr_5"),
    # path('user_pr_5/', views.user_details_5, name="user_pr_5"),
    path('user_pr_6/', views.user_details_6, name="user_pr_6"),


    path('error_404/', views.error_404,name="error_404"),
    path('error_403/', views.error_403,name="error_403"),

    # path('demo/', views.demo_fun,name="demo"),


    path('',views.AuthPage,name="auth"),
]