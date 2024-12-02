from rest_framework import serializers
from .models import Subject, Room, Participation

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'title', 'description', 'created_by', 'is_private']


class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = ['id', 'user_id', 'room_id', 'mic_allow', 'chat_allow', 'is_blocked']


class FileShareSerializer(serializers.Serializer):
    file = serializers.FileField()


class BlockUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()