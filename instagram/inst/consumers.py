import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Message, Profile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_user = self.scope["url_route"]["kwargs"]["username"]
        self.room_group_name = f"chat_{min(self.scope['user'].username, self.other_user)}_{max(self.scope['user'].username, self.other_user)}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender = self.scope["user"]

        # Save message to the database
        receiver = await sync_to_async(User.objects.get)(username=self.other_user)
        sender_profile = await sync_to_async(Profile.objects.get)(user=sender)
        receiver_profile = await sync_to_async(Profile.objects.get)(user=receiver)

        chat_message = await sync_to_async(Message.objects.create)(
            sender=sender_profile,
            receiver=receiver_profile,
            text=message
        )

        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender.username
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]

        # Send message to WebSocket (both sender & receiver will get it instantly)
        await self.send(text_data=json.dumps({
            "message": message,
            "sender": sender
        }))
