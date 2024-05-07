import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import Message


class PersonalChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        async_to_sync(
            self.send(text_data=json.dumps({
                'message': 'connected',
            }))
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))

    # async def receive(self, text_data=None, bytes_data=None):
    #     data = json.loads(text_data)
    #     print(data)
    #     message = data['message']
    #     username = data['username']
    #     receiver = data['receiver']
    #
    #     await self.save_message(username, self.room_group_name, message, receiver)
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name,
    #         {
    #             'type': 'chat_message',
    #             'message': text_data_json['message'],
    #         }
    #     )

    #
    # async def chat_message(self, event):
    #     message = event['message']
    #     username = event['username']
    #
    #     await self.send(text_data=json.dumps({
    #         'message': message,
    #         'username': username
    #     }))
    #


async def disconnect(self, code):
    self.channel_layer.group_discard(
        self.room_group_name,
        self.channel_name
    )


@database_sync_to_async
def save_message(self, conversation, sender, message_content):
    chat_obj = Message.objects.create(
        conversation=conversation,
        sender=sender,
        message_content=message_content
    )
    return chat_obj
