from django.urls import path
from profiles.views import user_recieved_pg
from . import views


urlpatterns = [
    path('profile',views.demo_pr, name="profile"),
    path('msg_pg',views.messages_pg, name="msg_pg"),
    path('send',views.user_send_pg, name="send"),
    path('accept',views.user_accept_pg, name="accept"),
    path('reject',views.user_reject_pg, name="reject"),
    path('recieved',views.user_recieved_pg, name="recieved"),





]