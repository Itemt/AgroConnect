from django.contrib import admin
from .models import Conversation, Message, Order

class MessageInline(admin.TabularInline):
    model = Message
    extra = 1

class ConversationAdmin(admin.ModelAdmin):
    inlines = [MessageInline]

admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message)
admin.site.register(Order)
