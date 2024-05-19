import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from chat.models import Conversation
from django.db.models import Q


class PersonalChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')
        self.room_group_name = 'chat_%s' % self.room_name
        user = self.scope['user']

        if user and user.is_authenticated:
            try:
                conversation = Conversation.objects.get(Q(user1=user.pk) | Q(user2=user.pk), pk=self.room_name)
            except Conversation.DoesNotExist:
                conversation = None

            if conversation:
                async_to_sync(self.channel_layer.group_add)(
                    self.room_group_name,
                    self.channel_name
                )
                self.accept()
                self.send(text_data=json.dumps({
                    'connect_message': 'Socket connected',
                }))
            else:
                self.close(code=4401)
        else:
            self.close(code=4401)

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


class FriendRequestConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            self.close()
        else:
            async_to_sync(self.channel_layer.group_add)(
                str(self.user.pk),
                self.channel_name
            )
            self.accept()

    def sent_friend_request(self, event):
        conversation = event['conversation']
        self.send(text_data=json.dumps({
            'conversation': conversation
        }))

    def cancel_friend_request(self, event):
        conversation = event['conversation']
        self.send(text_data=json.dumps({
            'conversation': conversation
        }))

    def accept_friend_request(self, event):
        conversation = event['conversation']
        self.send(text_data=json.dumps({
            'conversation': conversation
        }))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            str(self.user.pk),
            self.channel_name
        )
