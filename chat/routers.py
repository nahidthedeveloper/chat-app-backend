from django.urls import re_path
from chat.consumers import PersonalChatConsumer, FriendRequestConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', PersonalChatConsumer.as_asgi()),
    re_path(r'ws/friend_request/', FriendRequestConsumer.as_asgi()),
]
