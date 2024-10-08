from django.urls import re_path

from . import consumers, notification_consumer


websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>[a-zA-Z0-9_-]+)/$", consumers.ChatConsumer.as_asgi()),
    # re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/notification/(?P<room_name>[a-zA-Z0-9_-]+)/$", notification_consumer.Send_notification.as_asgi()),

]