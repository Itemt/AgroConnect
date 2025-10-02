import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
        
        is_participant = await self.is_user_participant()
        if not is_participant:
            await self.close()
        else:
            await self.channel_layer.group_add(
                self.conversation_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']

        new_message = await self.create_new_message(message_content)

        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_id': self.user.id,
                'sender_name': self.user.first_name,
                'timestamp': new_message.created_at.strftime('%d %b, %H:%M')
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def is_user_participant(self):
        conversation = Conversation.objects.filter(pk=self.conversation_id).first()
        return conversation and self.user in conversation.participants.all()

    @database_sync_to_async
    def create_new_message(self, content):
        return Message.objects.create(
            conversation_id=self.conversation_id,
            sender=self.user,
            content=content
        )
