from django.urls import path
from .import views


urlpatterns = [


    path('error_404/', views.error_404,name="error_404"),
    path('error_403/', views.error_403,name="error_403"),



    path('', views.SignupView.as_view(), name='auth_page'),
    path('login/', views.LoginView.as_view(), name='login'),

    
    path('otp/',views.CheckOTPView.as_view(),name="check_otp"),
    path('resend/',views.ResendOTPView.as_view(),name="resend"),
    path('logout/',views.UserLogout.as_view(),name="logout"),

    path('pass_reset/',views.ResetPassword.as_view(),name="pass_reset"),
    path('pass_reset_2/',views.ResetPassword_2.as_view(),name="pass_reset_2"),

    path('user_details/',views.UserPersonalDetailsView.as_view(),name="user_details"),
    path('job_details/', views.JobDetailsView.as_view(), name='job_details'),
    path('relation_type/', views.RelationShipGoalView.as_view(), name='relation_type'),
    path('additional_datas/', views.AdditionalDetailsView.as_view(), name="additional_datas"),
    path('check_type', views.UserType, name='check_type'),
    path('profile/', views.UserProfile.as_view(), name="profile"),
    path('profile_edit/', views.ProfileEdit.as_view(), name="profile_edit"),
    path('remove_files/<str:type>/<int:id>/', views.RemoveFiles.as_view(), name='remove_files'),
    path('change_pass/',views.ForgotPassword.as_view(),name="change_pass"),
    path('settings/', views.UserSetting.as_view(), name="settings"),
    path('privacy_setting_sec/', views.UserPartnerPreferenceView_2.as_view(), name="privacy_setting_sec"),
    path('privacy_setting/', views.UserPrivacySetting.as_view(), name="privacy_setting"),

]