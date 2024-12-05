import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room, RoomSubject
from .serializers import RoomSerializer
from asgiref.sync import sync_to_async
from django.forms.models import model_to_dict

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Tạo nhóm cho phòng để gửi thông báo cho tất cả các kết nối
        self.group_name = "rooms"

        # Tham gia nhóm phòng
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Chấp nhận kết nối WebSocket
        await self.accept()

        data = await self.get_active_room()

        await self.send(text_data=json.dumps({
            'type': 'initial_rooms',
            'messages': data
        }))


    async def disconnect(self, close_code):
        # Rời khỏi nhóm phòng khi kết nối bị ngắt
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Nhận thông báo từ nhóm và gửi qua WebSocket
    async def receive(self, text_data):
        # Xử lý dữ liệu nhận từ client (bao gồm thông báo tạo phòng)
        text_data_json = json.loads(text_data)
        if text_data_json['type'] == 'new_room':
            # Nhận thông tin phòng mới
            room_data = text_data_json['room']

            print(room_data)
            
            # Gửi thông báo về phòng mới cho tất cả các người dùng trong nhóm
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'send_room_update',
                    'room': room_data  # Gửi thông tin phòng mới đến nhóm
                }
            )

    # Gửi dữ liệu cập nhật lên nhóm
    async def send_room_update(self, event):
        room_data = event['room']
        
        # Gửi dữ liệu phòng mới cho tất cả các client
        await self.send(text_data=json.dumps({
            'type': 'new_room',
            'room': room_data  # Gửi thông tin phòng mới cho các client kết nối
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
