from django.urls import path

from . import views


urlpatterns = [
    path('profile/<int:user_id>/',views.UserProfileView.as_view(), name="profile"),
    # path('msg_pg',views.messages_pg.as_view(), name="msg_pg"),
    path('send/<int:pk>/',views.SendRequestView.as_view(), name="send_request"),
    path('sent/',views.SentedRequestView.as_view(), name="sented_request"),
    path('accept/',views.AcceptedRequestView.as_view(), name="accepted_request"),
    path('reject/',views.RejectedRequestView.as_view(), name="rejected_request"),
    path('received/',views.ReceivedRequestView.as_view(), name="received_request"),
    path('request-hanlde/<int:pk>/<str:action>/', views.HandleRequestView.as_view(), name='handle_request'),
    path("request/delete/<int:pk>", views.DeleteRequestView.as_view(), name="delete_request"),
    path('shortlist/', views.ShortlistView.as_view(), name='shortlist'),
    path('shortlist/add/<int:user_id>/', views.AddToShortlistView.as_view(), name='add_to_shortlist'),
    path('shortlist/remove/<int:user_id>/', views.RemoveFromShortlistView.as_view(), name='remove_from_shortlist'),
    path('shortlist_by/', views.ShortlistByView.as_view(), name='shortlist_by'),
    # path('chat',views.user_chat_pg, name="chat"),

    # path('contacted',views.user_contacted_pg, name="contacted"),
    # path('shortlisted',views.user_shortlisted_pg, name="shortlisted"),
    # path('shortlist',views.user_shortlist_pg, name="shortlist"),
    # path('pr_viewed',views.user_viewed_pg, name="pr_viewed"),
    
]