from rest_framework import serializers

from authentication.serializer import ProfileSerializer
from chat.models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    user1 = ProfileSerializer()
    user2 = ProfileSerializer()

    class Meta:
        model = Conversation
        fields = ['id', 'user1', 'user2', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
