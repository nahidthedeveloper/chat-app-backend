from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from authentication.serializer import EmptySerializer, Account, UsersSerializer
from chat.models import Conversation, Message
from chat.serializer import ConversationSerializer, MessageSerializer, CreateConversationSerializer
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
        if self.action == 'conversation_list':
            return ConversationSerializer
        if self.action == 'create_conversation':
            return CreateConversationSerializer
        elif self.action in ['sent_message', 'conversation']:
            return MessageSerializer
        return EmptySerializer

    def list(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='conversation_list')
    def conversation_list(self, request, *args, **kwargs):
        user = self.request.user
        try:
            sms = Conversation.objects.filter(Q(user1=user) | Q(user2=user))
        except Conversation.DoesNotExist:
            return Response(status=status.HTTP_403_FORBIDDEN)
        data = ConversationSerializer(sms, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_conversation/(?P<id>\d+)')
    def create_conversation(self, request, *args, **kwargs):
        user1 = request.user
        user2_id = kwargs.get('id')

        # Validate input data using serializer
        serializer = CreateConversationSerializer(data={'user1': user1.id, 'user2': user2_id})
        serializer.is_valid(raise_exception=True)

        user2 = Account.objects.filter(pk=user2_id).first()
        if not user2:
            return Response({"message": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
        ).first()

        if existing_conversation:
            return Response({"message": "Conversation already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create new conversation
        conversation = Conversation.objects.create(user1=user1, user2=user2, requester=user1)
        conversation_data = ConversationSerializer(conversation).data  # Serialize the conversation

        # Trigger channel
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            str(user2_id),
            {
                'type': 'sent_friend_request',
                'conversation': conversation_data,
            }
        )
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'], url_path=r'conversation/(?P<id>\d+)')
    def conversation(self, request, *args, **kwargs):
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
        if serializer.is_valid():
            conversation = serializer.validated_data.get('conversation')
            if not conversation.is_friend:
                return Response(
                    {'message': 'This user cannot be your friend. Please make friend first, then send the message.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
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

    @action(detail=False, methods=['POST'], url_path=r'accept_conversation/(?P<id>\d+)')
    def accept_conversation(self, request, *args, **kwargs):
        conversation_id = kwargs['id']
        user = request.user.pk
        requester = request.data['requester']
        if not conversation_id:
            return Response({"message": "Conversation id not found"}, status=status.HTTP_404_NOT_FOUND)
        if not requester:
            return Response({"message": "Requester not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            conversation = Conversation.objects.get(Q(user1=user) | Q(user2=user), pk=conversation_id)
        except Conversation.DoesNotExist:
            return Response("Conversation not found", status=status.HTTP_404_NOT_FOUND)

        if requester != user:
            conversation.is_friend = True
            conversation.is_pending = False
            conversation.save()

            conversation_data = ConversationSerializer(conversation).data
            receiver = None
            if user != conversation_data['user1']['id']:
                receiver = conversation_data['user1']['id']
            elif user != conversation_data['user2']['id']:
                receiver = conversation_data['user2']['id']

            # Trigger channel
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                str(receiver),
                {
                    'type': 'accept_friend_request',
                    'conversation': conversation_data,
                }
            )

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path=r'delete_conversation/(?P<id>\d+)')
    def delete_conversation(self, request, *args, **kwargs):
        conversation_id = kwargs['id']
        user = request.user.pk
        try:
            conversation = Conversation.objects.get(Q(user1=user) | Q(user2=user), pk=conversation_id)
        except Conversation.DoesNotExist:
            return Response("Conversation not found", status=status.HTTP_404_NOT_FOUND)

        if conversation:
            conversation_data = ConversationSerializer(conversation).data
            receiver = None
            if user != conversation_data['user1']['id']:
                receiver = conversation_data['user1']['id']
            elif user != conversation_data['user2']['id']:
                receiver = conversation_data['user2']['id']

            conversation.delete()

            # Trigger channel
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                str(receiver),
                {
                    'type': 'cancel_friend_request',
                    'conversation': conversation_data,
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
