from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Room, Participation, Subject
from apps.accounts.models import User
from .serializers import SubjectSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class ToggleMicView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        try:
            # Kiểm tra nếu người dùng tham gia phòng học
            participation = Participation.objects.get(user_id=request.user, room_id=room_id)

            # Chuyển trạng thái mic_allow
            participation.mic_allow = not participation.mic_allow
            participation.save()

            # Trả về mã trạng thái HTTP 200 OK
            return Response({'mic_allow': participation.mic_allow}, status=status.HTTP_200_OK)

        except Participation.DoesNotExist:
            return Response({'error': 'You are not a participant of this room'}, status=status.HTTP_403_FORBIDDEN)


class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        try:
            # Tìm phòng học theo ID
            room = Room.objects.get(id=room_id)
            creator = room.created_by
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

        # Kiểm tra xem người gọi API có phải là chủ phòng không
        if creator != request.user:
            return Response({'error': 'Only the room creator can block users'}, status=status.HTTP_403_FORBIDDEN)

        # Lấy thông tin người dùng cần block từ request
        user_to_block = User.objects.get(id=request.data.get('user_id'))
        try:
            # Tìm tham gia phòng của người dùng cần block
            participation = Participation.objects.get(room_id=room, user_id=user_to_block)
        except Participation.DoesNotExist:
            return Response({'error': 'User is not a participant in this room'}, status=status.HTTP_404_NOT_FOUND)

        # Đánh dấu người dùng là bị block
        participation.is_blocked = True
        participation.time_out = timezone.now()  # Đánh dấu thời gian rời khỏi phòng
        participation.save()

        # Cập nhật thông tin tham gia của người bị block (có thể xóa tham gia nếu cần)
        # Hoặc, bạn có thể chỉ cần trả về thông báo là người dùng bị block và rời khỏi phòng.

        return Response({'message': f'User {user_to_block.username} has been blocked and logged out of the room'},
                        status=status.HTTP_200_OK)