from django.urls import path
from . import views


urlpatterns = [

    path('user_pr/', views.user_details, name="user_pr"),
    path('user_pr_2/', views.user_details_2, name="user_pr_2"),
    path('user_pr_3/', views.user_details_3, name="user_pr_3"),
    path('user_pr_4/', views.user_details_4, name="user_pr_4"),
    path('user_pr_5/', views.user_details_5, name="user_pr_5"),
    # path('user_pr_5/', views.user_details_5, name="user_pr_5"),

    path('error_404/', views.error_404,name="error_404"),
    path('error_403/', views.error_403,name="error_403"),
    path('select/', views.multiselect,name="select"),


    path('', views.SignupView.as_view(), name='auth_page'),
    path('login/', views.LoginView.as_view(), name='login'),

    
    path('otp/',views.CheckOTPView.as_view(),name="check_otp"),
    path('resend/',views.ResendOTPView.as_view(),name="resend"),
    path('logout/',views.UserLogout.as_view(),name="logout"),

    path('forgot_password/',views.ForgotPassword.as_view(),name="forgot_password"),
    path('pass_reset/',views.ResetPassword.as_view(),name="pass_reset"),
    path('pass_reset_2/',views.ResetPassword_2.as_view(),name="pass_reset_2"),

    path('user_details/',views.UserPersonalDetailsView.as_view(),name="user_details"),
    path('job_details/', views.JobDetailsView.as_view(), name='job_details'),
    path('relation_type/', views.RelationShipGoalView.as_view(), name='relation_type'),
    path('additional_datas/', views.AdditionalDetailsView.as_view(), name="additional_datas"),
    path('check_type', views.UserType, name='check_type'),
    path('privacy_setting_sec/', views.UserPartnerPreferenceView_2.as_view(), name="privacy_setting_sec"),
]