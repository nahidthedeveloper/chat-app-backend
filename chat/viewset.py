from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from authentication.serializer import EmptySerializer
from chat.models import Conversation, Message
from chat.serializer import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = []
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'conversation':
            return ConversationSerializer
        return EmptySerializer

    def list(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='conversation')
    def conversation(self, request, *args, **kwargs):
        user = self.request.user
        sms = Conversation.objects.filter(user1=user) | Conversation.objects.filter(user2=user)
        data = ConversationSerializer(sms, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='messages/(?P<id>\d+)')
    def messages(self, request, *args, **kwargs):
        sms = Message.objects.filter(conversation=kwargs['id']).order_by('-timestamp')
        data = MessageSerializer(sms, many=True).data
        return Response(data, status=status.HTTP_200_OK)
