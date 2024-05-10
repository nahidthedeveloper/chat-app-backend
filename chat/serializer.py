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
        if conversation['is_friend'] is True:
            message = Message.objects.create(conversation=conversation, sender=sender,
                                             message=validated_data['message'])
        else:
            return Response(
                {'message': 'This user cannot be your friend. Please make friend first, then send the message.'},
                status=status.HTTP_400_BAD_REQUEST)
        return message
