from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Chat, Message  # Make sure to import your Message model
from django.utils import timezone  # For timestamp
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        # Fetch the chat object asynchronously
        self.chat = await database_sync_to_async(Chat.objects.get)(id=self.chat_id)
        
        # Join the chat room group
        self.room_group_name = f"chat_{self.chat_id}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the chat group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['content']
        sender_email = text_data_json['sender'] 
        reciever_email = text_data_json['reciever']  # Expecting email or username here
        
        # Save the message asynchronously
        await self.save_message(message_content, sender_email,reciever_email)

        # Broadcast the message to the chat group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender': sender_email, 
                'timestamp': str(timezone.now())  
            }
    )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

 
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def save_message(self, content, sender_email,reciever_email):
       
        sender = User.objects.get(username=sender_email) 
        reciever = User.objects.get(username=reciever_email)
       
        chat=Chat.objects.get(user=reciever.id)
      
        
        message = Message(
            chat=chat,
            sender=sender,  
            content=content,
            timestamp=timezone.now()  
        )
        message.save()
