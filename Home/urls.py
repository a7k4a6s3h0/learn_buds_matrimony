from django.urls import path
from . import views


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('qualification', views.Qualification.as_view(), name='qualification'),
    path('loaction', views.Loaction.as_view(), name='loaction'),
    path('designation', views.Designation.as_view(), name='designation'),
    path('profiles/filter', views.FilterPrifles.as_view(), name='filter_prifles'),
    # path('error404', views.error404.as_view(), name="error404"),
]