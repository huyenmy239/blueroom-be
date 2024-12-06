from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'user', 'content', 'timestamp', 'type']

    def get_user(self, obj):
        return obj.participation_id.user_id.username