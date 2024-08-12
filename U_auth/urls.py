from django.urls import path
from U_auth.views import user_details_3
from . import views


urlpatterns = [
    # path('',views.demo,),
    path('login/',views.login_view,name="login"),
    path('perdet/',views.perdet_view,name="personal details"),
    path('jobst/',views.jobst,name="job status"),
    path('jobd/',views.jobd,name="job details"),
    path('jobd1/',views.jobd1,name="job details1"),
    path('relation/',views.relation,name="Relationship"),
    path('interest/',views.interest,name="Interested"),
    path('adddet/', views.adddet, name="Additional Details"),
    path('user_pr/', views.user_details, name="user_pr"),
    path('user_pr_2/', views.user_details_2, name="user_pr_2"),
    path('user_pr_3/', views.user_details_3, name="user_pr_3"),
    path('user_pr_4/', views.user_details_4, name="user_pr_4"),
    path('user_pr_5/', views.user_details_5, name="user_pr_5"),
    # path('user_pr_5/', views.user_details_5, name="user_pr_5"),
    path('user_pr_6/', views.user_details_6, name="user_pr_6"),





    path('',views.AuthPage,name="auth"),
]