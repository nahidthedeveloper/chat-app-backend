from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from authentication.serializer import EmptySerializer
from django.shortcuts import get_object_or_404
from authentication.models import Account
from chat.models import Conversation, Message
from chat.serializer import ConversationSerializer, MessageSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'conversation':
            return ConversationSerializer
        elif self.action in ['messages', 'sent_message']:
            return MessageSerializer
        return EmptySerializer

    def list(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='conversation')
    def conversation(self, request, *args, **kwargs):
        user = self.request.user
        sms = Conversation.objects.filter(user1=user) | Conversation.objects.filter(user2=user)
        data = ConversationSerializer(sms, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'messages/(?P<id>\d+)')
    def messages(self, request, *args, **kwargs):
        sms = Message.objects.filter(conversation=kwargs['id']).order_by('-timestamp')
        data = MessageSerializer(sms, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'sent_message/(?P<id>\d+)')
    def sent_message(self, request, *args, **kwargs):
        payload = {
            'conversation': kwargs['id'],
            'message': request.data['message'],
            'sender': request.user.pk,
        }
        serializer = MessageSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{kwargs['id']}',
            {
                'type': 'chat_message',
                'message': serializer.data,
            }
        )
        return Response(status=status.HTTP_200_OK)
