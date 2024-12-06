import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room, RoomSubject
from .serializers import RoomSerializer
from asgiref.sync import sync_to_async
from django.forms.models import model_to_dict

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "rooms"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        data = await self.get_active_room()

        await self.send(text_data=json.dumps({
            'type': 'initial_rooms',
            'messages': data
        }))


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['type'] == 'new_room':
            room_data = text_data_json['room']

            print(room_data)
            
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'send_room_update',
                    'room': room_data
                }
            )

    async def send_room_update(self, event):
        room_data = event['room']
        
        await self.send(text_data=json.dumps({
            'type': 'new_room',
            'room': room_data
        }))


    @sync_to_async
    def get_active_room(self):
        rooms = Room.objects.filter(is_active=True).order_by('-created_at')

        print(rooms)
        rooms_data = []

        for room in rooms:
            subjects = RoomSubject.objects.filter(room_id=room.id)
            subject_data = [{
                "id": subject.subject_id.id,
                "name": subject.subject_id.name
            } for subject in subjects]
            rooms_data += [{
                "id": room.id,
                "title": room.title,
                "description": room.description,
                "created_by": room.created_by.username,
                "created_at": str(room.created_at),
                "members": room.members,
                "background": str(room.background.bg),
                "subjects": subject_data
            }]

        return rooms_data
