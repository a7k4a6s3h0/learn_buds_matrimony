from django.urls import path

from . import views


urlpatterns = [
    path('profile/<int:user_id>/',views.UserProfileView.as_view(), name="profile"),
    path('send/<int:pk>/',views.SendRequestView.as_view(), name="send_request"),
    path('sent/',views.SentedRequestView.as_view(), name="sented_request"),
    path('accept/',views.AcceptedRequestView.as_view(), name="accepted_request"),
    path('reject/',views.RejectedRequestView.as_view(), name="rejected_request"),
    path('received/',views.ReceivedRequestView.as_view(), name="received_request"),
    path('request-hanlde/<int:pk>/<str:action>/', views.HandleRequestView.as_view(), name='handle_request'),
    path("request/delete/<int:pk>", views.DeleteRequestView.as_view(), name="delete_request"),

    
]