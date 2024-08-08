from django.urls import path
from . import views


urlpatterns = [
    path('profile',views.demo_pr, name="profile"),
]