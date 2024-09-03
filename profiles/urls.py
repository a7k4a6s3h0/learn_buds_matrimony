from django.urls import path

from . import views


urlpatterns = [
    path('profile/<int:user_id>/',views.demo_pr, name="profile"),
    path('msg_pg',views.messages_pg, name="msg_pg"),
    # path('send',views.user_send_pg, name="send"),
    # path('accept',views.user_accept_pg, name="accept"),
    # path('reject',views.user_reject_pg, name="reject"),
    # path('recieved',views.user_recieved_pg, name="recieved"),
    path('chat',views.user_chat_pg, name="chat"),

    path('contacted',views.user_contacted_pg, name="contacted"),
    path('shortlisted',views.user_shortlisted_pg, name="shortlisted"),
    path('shortlist',views.user_shortlist_pg, name="shortlist"),
    path('pr_viewed',views.user_viewed_pg, name="pr_viewed"),
    









]