from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from authentication.serializer import EmptySerializer, Account, ProfileSerializer, UsersSerializer
from chat.models import Conversation, Message
from chat.serializer import ConversationSerializer, MessageSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


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

    @action(detail=False, methods=['POST'], url_path=r'create_conversation/(?P<id>\d+)')
    def create_conversation(self, request, *args, **kwargs):
        user1 = self.request.user
        user2 = kwargs['id']
        find_conversation = Conversation.objects.filter(
            Q(user1=user1, user2_id=user2) | Q(user1=user2, user2=user1)).first()

        if not find_conversation:
            if user1 == user2:
                return Response({'message': 'How funny !! You can not friend with yourself.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user2:
                try:
                    user2 = Account.objects.get(pk=user2)
                except Account.DoesNotExist:
                    return Response({"message": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message": "Please provide receiver."},
                                status=status.HTTP_400_BAD_REQUEST)

            Conversation.objects.create(user1=user1, user2=user2, requester=user1)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status.HTTP_400_BAD_REQUEST)

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

        # Trigger channel
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{kwargs['id']}',
            {
                'type': 'chat_message',
                'message': serializer.data,
            }
        )
        return Response(status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = []
    serializer_class = UsersSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def get_queryset(self):
        user = self.request.user
        if self.action == 'list':
            return Account.objects.exclude(Q(pk=user.id) | Q(is_superuser=True)).all()
        return []

    def get_serializer_class(self):
        if self.action == 'list':
            return UsersSerializer
        return EmptySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
