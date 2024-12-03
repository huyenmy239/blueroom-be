from .serializers import SubjectSerializer, BackgroundSerializer, RoomSerializer, EditRoomSerializer, EditPermissionSerializer, ParticipationSerializer
from .permissions import IsAdminUser, IsRoomOwner
from .models import Subject, Background, Room, Participation, User, RoomSubject
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now, timezone
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum

from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.accounts.models import User

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()

class BackgroundViewSet(viewsets.ModelViewSet):
    queryset = Background.objects.all()
    serializer_class = BackgroundSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()

@permission_classes([AllowAny])
class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    permission_classes = [IsRoomOwner]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return EditRoomSerializer
        return RoomSerializer

    def perform_create(self, serializer):
        if self.request.user.is_busy:
                raise ValidationError("Bạn đang trong phòng, không thể tạo phòng mới.")

        room = serializer.save(created_by=self.request.user)

        Participation.objects.create(
            user_id=self.request.user,
            room_id=room,
            time_in=now()
        )
        
        self.request.user.is_busy = True
        self.request.user.save()
        room.members = 1
        room.save()

    def perform_update(self, serializer):
        room = self.get_object()  
        if room.created_by != self.request.user:
            raise PermissionDenied("Chỉ chủ phòng mới có quyền cập nhật thông tin phòng.")
        serializer.save()

    @action(detail=False, methods=['get'], url_path='room-active')
    def list_Room_Active(self, request):
        active_rooms = Room.objects.filter(is_active=True).order_by('-created_at')

        query = request.query_params.get('query', None) 
        if query:
            # Lọc theo 'title' 
            active_rooms_title = active_rooms.filter(title__icontains=query)
            
            if active_rooms_title.exists():
                active_rooms = active_rooms_title
            else:
                # Nếu không có kết quả, lọc theo 'subject_name'
                room_subjects = RoomSubject.objects.filter(subject_id__name__icontains=query)
                
                # Lọc các phòng học có chủ đề tương ứng thông qua room_id
                active_rooms = active_rooms.filter(id__in=room_subjects.values('room_id'))
            
        serializer = RoomSerializer(active_rooms, many=True)
        return Response(serializer.data)


    @action(detail=True, methods=['get'], url_path='members-in-room')
    def list_members_in_room(self, request, pk=None):
        room = self.get_object()

        participations = Participation.objects.filter(room_id=room, time_out__isnull=True)

        serializer = ParticipationSerializer(participations, many=True, context={'request': request})

        return Response(serializer.data)
        
    
    @action(detail=True, methods=['post'], url_path='join')
    def join_room(self, request, pk=None):
        """Tham gia phòng học."""
        room = self.get_object()
        user = request.user
        
        
        if user.is_busy:
            return Response({"message": "Bạn đang tham gia phòng khác, không thể tham gia thêm phòng."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if not room.is_active:
            return Response({"message": "Phòng học đã kết thúc."},
                            status=status.HTTP_400_BAD_REQUEST)

        participation = Participation.objects.filter(user_id=user, room_id=room).first()

        if participation and participation.is_blocked == room.id:
            return Response(
                {"message": "Bạn đã bị cấm tham gia phòng này."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Kiểm tra nếu phòng là riêng tư
        # if room.is_private:
        #     return Response({"message": "Phòng riêng tư, chờ xác nhận từ chủ phòng."},
        #                     status=status.HTTP_202_ACCEPTED)

        

        if participation:
            participation.time_in = now() 
            participation.time_out = None 
            participation.save()  

            user.is_busy = True
            user.save()

            room.members += 1
            room.save()
            return Response({"message": "Bạn đã tham gia lại phòng này."}, status=status.HTTP_200_OK)
        else:
            participation = Participation.objects.create(
                user_id=user,
                room_id=room,
                time_in=now()  
            )
            user.is_busy = True
            user.save()

            room.members += 1
            room.members_max += 1
            room.save()
            return Response({"message": "Bạn đã tham gia phòng thành công."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='leave')
    def leave_room(self, request, pk=None):
        """Rời phòng học."""
        room = self.get_object()
        user = request.user

        try:
            participation = Participation.objects.get(user_id=user, room_id=room)
        except Participation.DoesNotExist:
            return Response({"message": "Bạn chưa tham gia phòng này."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Chủ phòng rời, đóng phòng
        if room.created_by == user:
            room.is_active = False
            room.members = 1
            room.save()

            other_participants = Participation.objects.filter(room_id=room)

            other_participants.update(time_out=now())
            other_participants_user_ids = other_participants.values_list('user_id', flat=True)

            User.objects.filter(id__in=other_participants_user_ids).update(is_busy=False)

            return Response(
                {"message": "Phòng đã đóng do chủ phòng rời khỏi. Tất cả người dùng đã bị văng khỏi phòng."},
                status=status.HTTP_200_OK
            )
        
        # Người dùng thông thường rời phòng
        participation.time_out = now()
        participation.save()

        user.is_busy = False
        user.save()

        # Giảm số lượng thành viên trong phòng
        room.members -= 1
        room.save()

        return Response({"message": "Bạn đã rời khỏi phòng thành công."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='edit-permissions')
    def edit_permissions(self, request, pk=None):
        """Chỉnh sửa quyền mic_allow, chat_allow, is_blocked của một User trong phòng."""
        room = self.get_object()
        user = request.user

        # Kiểm tra nếu người dùng là chủ phòng
        if room.created_by != user:
            return Response(
                {"message": "Bạn không có quyền chỉnh sửa quyền của người dùng khác trong phòng này."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = EditPermissionSerializer(data=request.data, context={'room': room})
        if serializer.is_valid():
            participation = Participation.objects.get(user_id=request.data['user_id'], room_id=room)
            serializer.update(participation, serializer.validated_data)

            return Response({"message": "Quyền của người dùng đã được cập nhật."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'], url_path="account-report")
    def reports(self, request, *args, **kwargs):
        total_account = User.objects.filter(is_admin=False).count()
        total_account_in_room = Participation.objects.filter(time_out__isnull=False).values('user_id').distinct().count()

        data = {
            "total_account": total_account,
            "account_in_room": total_account_in_room
        }
        return Response(data)
    
    @action(detail=False, methods=["get"], url_path="type-room-report")
    def type_room(self, request, *args, **kwargs):
        total_room_active = Room.objects.filter(is_active=True).count()
        total_private_active = Room.objects.filter(is_active=True, is_private=True).count()

        data = {
            "total_room_active": total_room_active,
            "total_private_room": total_private_active
        }

        return Response(data)
    
    @action(detail=False, methods=["get"], url_path="room-active-report")
    def room_active(self, request, *args, **kwargs):
        total_room = Room.objects.all().count()
        total_room_active = Room.objects.filter(is_active=True).count()

        data = {
            "total_room": total_room,
            "total_room_active": total_room_active
        }

        return Response(data)
    
    @action(detail=False, methods=["post"], url_path="room-created-report")
    def room_created(self, request, *args, **kwargs):
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except (TypeError, ValueError):
            return Response({"error": "Invalid date format. Use 'YYYY-MM-DD'."}, status=400)

        rooms = Room.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)

        # Serialize danh sách các phòng
        serializer = RoomSerializer(rooms, many=True)

        data = {
            "total_rooms_created": rooms.count(),
            "rooms_created": serializer.data
        }
        return Response(data)
        
    @action(detail=False, methods=["post", "get"], url_path="room-popular-report")
    def room_popular(self, request, *args, **kwargs):
        try:
            n_rooms = int(request.query_params.get("n", 10))
        except ValueError:
            return Response({"error": "Parameter 'n' must be an integer."}, status=400)

        popular_rooms = (
            Room.objects.filter(is_active=True)
            .order_by('-members')[:n_rooms]  # Lấy n phòng đầu tiên
        )

        # Serialize danh sách phòng
        serializer = RoomSerializer(popular_rooms, many=True)

        data = {
            "total_rooms": len(popular_rooms),
            "rooms": serializer.data
        }
        return Response(data)



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
