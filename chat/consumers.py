import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User


class PersonalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(self.scope)
        # my_id = self.scope['user'].id
        # other_user_id = self.scope['url_route']['kwargs']['id']
        # if int(my_id) > int(other_user_id):
        #     self.room_name = f'{my_id}-{other_user_id}'
        # else:
        #     self.room_name = f'{other_user_id}-{my_id}'
        #
        # self.room_group_name = 'chat_%s' % self.room_name
        #
        # await self.channel_layer.group_add(
        #     self.room_group_name,
        #     self.channel_name
        # )
        print("Testing connection on redis")
        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Broadcast the received message to all clients
        await self.send(text_data=json.dumps({
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
    #     await self.channel_layer.group_send(
    #         self.room_group_name,
    #         {
    #             'type': 'chat_message',
    #             'message': message,
    #             'username': username,
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
    # async def disconnect(self, code):
    #     self.channel_layer.group_discard(
    #         self.room_group_name,
    #         self.channel_name
    #     )
