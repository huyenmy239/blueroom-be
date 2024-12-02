from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Message, Participation
from .serializers import MessageSerializer
from apps.rooms.serializers import FileShareSerializer
from apps.rooms.models import Room

# Create your views here.


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
            participation = Participation.objects.get(room_id=room, user_id=request.user)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        except Participation.DoesNotExist:
            return Response({'error': 'Participation not found'}, status=status.HTTP_404_NOT_FOUND)

        message = Message(
            participation_id=participation,
            content=request.data.get('message'),
            type='text',
        )
        message.save()
        
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
    

class GetMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

        messages = Message.objects.filter(participation_id__room_id=room.id).order_by('timestamp')
        return Response(MessageSerializer(messages, many=True).data)
    

class ShareFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
            participation = Participation.objects.get(room_id=room, user_id=request.user)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        except Participation.DoesNotExist:
            return Response({'error': 'Participation not found'}, status=status.HTTP_404_NOT_FOUND)

        file_serializer = FileShareSerializer(data=request.data)
        if file_serializer.is_valid():
            file = file_serializer.validated_data['file']
            message = Message(
                participation_id=participation,
                content=f'File shared: {file.name}',
                type='file',
            )
            message.save()
            
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)