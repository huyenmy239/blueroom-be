from rest_framework import serializers
from .models import Background, Subject, Room, RoomSubject, Participation
from django.utils.timezone import now
from django.db.models import Count

class BackgroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Background
        fields = ['id', 'bg']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

class RoomSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    class Meta:
        model = RoomSubject
        fields = ['subject']

class RoomSerializer(serializers.ModelSerializer):
    subjects = serializers.SerializerMethodField()  # Tạo trường tuỳ chỉnh
    background = BackgroundSerializer(read_only=True)
    created_by = serializers.StringRelatedField(source='created_by.username', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'title', 'description', 'created_by', 'created_at', 'is_private', 
                  'background', 'enable_mic', 'members', 'subjects', 'is_active']

    def get_subjects(self, obj):
        subjects = Subject.objects.filter(rooms__room_id=obj)
        return SubjectSerializer(subjects, many=True).data

class EditRoomSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), 
        many=True,  
        write_only=True, 
        required=False  
    )

    class Meta:
        model = Room
        fields = ['id', 'title', 'subject', 'background', 'description', 'is_private', 'enable_mic']

    def create(self, validated_data):
        # Lấy danh sách subject từ validated_data
        subjects = validated_data.pop('subject', [])
        # Tạo room
        request = self.context['request']
        validated_data['created_by'] = request.user 
        room = Room.objects.create(**validated_data)

        # Tạo các đối tượng RoomSubject liên kết với các subject đã chọn
        for subject in subjects:
            RoomSubject.objects.create(room_id=room, subject_id=subject)

        return room

class EditPermissionSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField()
    mic_allow = serializers.BooleanField(required=False)
    chat_allow = serializers.BooleanField(required=False)
    is_blocked = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Participation
        fields = ['user_id', 'mic_allow', 'chat_allow', 'is_blocked']

    def validate(self, attrs):
        """
        Xác minh dữ liệu hợp lệ.
        """
        user_id = attrs.get('user_id')
        room = self.context.get('room')

        try:
            participation = Participation.objects.get(user_id=user_id, room_id=room)
        except Participation.DoesNotExist:
            raise serializers.ValidationError({"user_id": "Người dùng này không tồn tại trong phòng."})

        is_blocked = attrs.get('is_blocked')
        if is_blocked is not None and is_blocked != room.id:
            raise serializers.ValidationError({"is_blocked": "Chỉ có thể chặn người dùng trong phòng hiện tại."})

        return attrs

    def update(self, instance, validated_data):
        """
        Cập nhật thông tin quyền trong Participation.
        """
        instance.mic_allow = validated_data.get('mic_allow', instance.mic_allow)
        instance.chat_allow = validated_data.get('chat_allow', instance.chat_allow)
        instance.is_blocked = validated_data.get('is_blocked', instance.is_blocked)

        room = instance.room_id
        user = instance.user_id

        # Nếu bị chặn, cập nhật thời gian thoát
        if instance.is_blocked == room.id:
            instance.time_out = now()
            room.members = max(0, room.members - 1)
            room.save()

            user.is_busy = False
            user.save()

        instance.save()
        return instance

class ParticipationSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Participation
        fields = ['id', 'user', 'time_in', 'mic_allow', 'chat_allow', 'is_blocked']

    def get_user(self, obj):
        return {
            "id": obj.user_id.id,
            "username": obj.user_id.username,
            "avatar": self.context['request'].build_absolute_uri(obj.user_id.avatar.url)
            if obj.user_id.avatar else None
        }


class FileShareSerializer(serializers.Serializer):
    file = serializers.FileField()


class BlockUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
