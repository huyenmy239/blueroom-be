from .serializers import SubjectSerializer, BackgroundSerializer, RoomSerializer, EditRoomSerializer, EditPermissionSerializer, RoomActivitySerializer, ParticipationSerializer
from .permissions import IsAdminUser, IsRoomOwner
from .models import Subject, Background, Room, Participation, User, RoomSubject
from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum

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
    def listRoomActive(self, request):
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

    @action(detail=False, methods=['get'], url_path='room-activity')
    def room_activity(self, request):
        """
        Lấy báo cáo tổng hợp về hoạt động phòng học.
        """
        # Tổng số phòng học
        total_rooms = Room.objects.count()

        total_participants = Room.objects.aggregate(total_participants=Sum('members_max'))['total_participants']

        # Các phòng gần đây
        recent_rooms = Room.objects.annotate(
            participants_count=Count('participants')
        ).order_by('-created_at')[:10]  

        data = {
            "total_rooms": total_rooms,
            "total_participants": total_participants,
            "recent_rooms": RoomActivitySerializer(recent_rooms, many=True).data
        }

        return Response(data)
    
    # @action(detail=False, methods=['get'], url_path='private-rooms')
    # def private_rooms(self, request):
    #     """
    #     Lấy báo cáo về các phòng riêng (Private Rooms).
    #     """
    #     private_rooms = Room.objects.filter(is_private=True)

    #     data = {
    #         "private_rooms": PrivateRoomSerializer(private_rooms, many=True).data
    #     }

    #     return Response(data)

    # @action(detail=False, methods=['get'], url_path='user-activity')
    # def user_activity(self, request):
    #     """
    #     Lấy báo cáo về hoạt động người dùng.
    #     """
    #     user_activity = Participation.objects.filter(time_out__isnull=True).values('user_id').annotate(
    #         total_participation=Count('user_id')
    #     )

    #     data = {
    #         "user_activity": user_activity
    #     }

    #     return Response(data)