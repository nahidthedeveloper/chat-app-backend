import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import Message, Conversation
from authentication.models import Account


class PersonalChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        self.send(text_data=json.dumps({
            'connect_message': 'Socket connected',
        }))

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

    # Send a welcome message when connected
    # self.send(text_data=json.dumps({
    #     'message': 'Socket connected',
    # }))

    # def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']
    #     sender = text_data_json['sender']
    #
    #     # Save message to the database
    #     # self.save_message(message, sender)
    #
    #     # Broadcast message to room group
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name,
    #         {
    #             'type': 'chat_message',
    #             'message': message,
    #             'sender': sender
    #         }
    #     )
    #
    # def chat_message(self, event):
    #     message = event['message']
    #     sender = event['sender']
    #     # Send message to WebSocket
    #     self.send(text_data=json.dumps({
    #         'message': message,
    #         'sender': sender
    #     }))

    # def save_message(self, message, sender_id):
    #     try:
    #         sender = Account.objects.get(pk=sender_id)
    #     except Account.DoesNotExist:
    #         print('Sender does not exist')
    #         return
    #
    #     try:
    #         conversation = Conversation.objects.get(pk=self.room_name)
    #     except Conversation.DoesNotExist:
    #         print('Conversation does not exist')
    #         return
    #
    #     Message.objects.create(
    #         conversation=conversation,
    #         sender=sender,
    #         message=message
    #     )
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
