from django.urls import re_path
from chat.consumers import PersonalChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', PersonalChatConsumer.as_asgi()),
]
