from rest_framework import serializers

from authentication.models import Account
from authentication.serializer import ProfileSerializer
from chat.models import Conversation, Message
from rest_framework.response import Response
from rest_framework import status


class ConversationSerializer(serializers.ModelSerializer):
    user1 = ProfileSerializer(read_only=True)
    user2 = ProfileSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = ('id', 'user1', 'user2', 'requester', 'is_friend', 'is_pending', 'created_at', 'updated_at')


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
        return Message.objects.create(
            conversation=conversation,
            sender=sender,
            message=validated_data['message']
        )


class CreateConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['user1', 'user2']

    def validate(self, attrs):
        user1 = attrs.get('user1')
        user2 = attrs.get('user2')

        if user1 is None:
            raise serializers.ValidationError({'user1': 'User1 is required'})
        if user2 is None:
            raise serializers.ValidationError({'user2': 'User2 is required'})
        if user1 == user2:
            raise serializers.ValidationError("You can't friend with yourself.")
        return attrs
