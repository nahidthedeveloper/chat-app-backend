from rest_framework import serializers

from authentication.models import Account
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

    def validate(self, attrs):
        if attrs['message'] is None:
            raise serializers.ValidationError({'message': 'Message is required'})
        if attrs['conversation'] is None:
            raise serializers.ValidationError({'conversation': 'Conversation is required'})
        if attrs['sender'] is None:
            raise serializers.ValidationError({'sender': 'Sender is required'})
        return attrs

    def create(self, validated_data):
        sender = Account.objects.get(pk=validated_data['sender'].pk)
        conversation = Conversation.objects.get(pk=validated_data['conversation'].pk)
        message = Message.objects.create(conversation=conversation, sender=sender, message=validated_data['message'])
        return message
