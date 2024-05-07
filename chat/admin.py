from django.contrib import admin

from chat.models import Conversation, Message


class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user1', 'user2']


class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender']


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
