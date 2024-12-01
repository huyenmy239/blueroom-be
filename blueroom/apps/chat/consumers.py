import json
from .models import Message
from apps.rooms.models import Participation
from apps.accounts.models import User
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async




class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Lấy room_name từ URL hoặc các thông tin khác
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'roomchat_{self.room_id}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept WebSocket connection
        await self.accept()

        messages_data = await self.get_messages(self.room_id)

        await self.send(text_data=json.dumps({
            'type': 'initial_messages',
            'messages': messages_data
        }))
    

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Parse the incoming message
        text_data_json = json.loads(text_data)
        type = text_data_json.get('type', '')
        
        print(text_data_json)
        content = text_data_json.get('content')

        
        
        if type == 'offer':
            # Handle the offer from client
            offer = text_data_json.get('offer')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'offer',
                    'offer': offer
                }
            )
        elif type == 'answer':
            # Handle the answer from client
            answer = text_data_json.get('answer')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'answer',
                    'answer': answer
                }
            )
        elif type == 'candidate':
            # Handle ICE candidates from client
            candidate = text_data_json.get('candidate')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'candidate',
                    'candidate': candidate
                }
            )
        elif type == 'message':
            # Handle chat message
            # chat_message = text_data_json.get('message')
            username = text_data_json.get('user')

            user = await self.get_user(username)

            message = await self.create_message(user, content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': content,
                    'user': user.username
                }
            )

    async def offer(self, event):
        # Send offer to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'offer': event['offer']
        }))

    async def answer(self, event):
        # Send answer to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'answer': event['answer']
        }))

    async def candidate(self, event):
        # Send ICE candidate to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'candidate',
            'candidate': event['candidate']
        }))

    async def chat_message(self, event):
        # Send chat message to WebSocket
        print(event['user'])
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'user': event['user']
        }))


    @sync_to_async
    def get_messages(self, room_id):
        messages = Message.objects.filter(participation_id__room_id=room_id).order_by('timestamp')
    
    # Chuyển dữ liệu sang dạng list để dễ xử lý trong async context
        messages_data = [{
            'message': message.content,
            'user': message.participation_id.user_id.username,
            'message_type': message.type
        } for message in messages]

        return messages_data


    @sync_to_async
    def get_user(self, username):
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return None
    

    @sync_to_async
    def create_message(self, user, content):
        return Message.objects.create(
                participation_id=Participation.objects.get(room_id=self.room_id, user_id=user),
                content=content,
                type='text',
            )