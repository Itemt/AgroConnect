import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f'user_{self.user.id}_notifications'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notification_message(self, event):
        # Forward notification payload to client
        await self.send(text_data=json.dumps({
            'title': event.get('title'),
            'message': event.get('message'),
            'category': event.get('category'),
            'order_id': event.get('order_id'),
            'payment_id': event.get('payment_id'),
            'created_at': event.get('created_at'),
        }))


