from django.urls import path
from . import views


urlpatterns = [
    path('',views.demo,),
    path('login/',views.login_view,name="login"),
    path('perdet/',views.perdet_view,name="personal details"),
    path('jobst/',views.jobst,name="job status"),
    path('jobd/',views.jobd,name="job details"),
    path('jobd1/',views.jobd1,name="job details1"),
    path('relation/',views.relation,name="Relationship"),
    path('interest/',views.interest,name="Interested"),
    path('adddet/', views.adddet, name="Additional Details")
]