from django.db import models
from authentication.models import Account
from django.db.models import Q


class ConversationManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(user1=user) | Q(user2=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Conversation(models.Model):
    user1 = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='conversations_as_user1')
    user2 = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='conversations_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ConversationManager()

    class Meta:
        unique_together = ['user1', 'user2']


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(Account, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

