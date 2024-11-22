from django.db import models
from accounts.models import User


# Create your models here.

class Background(models.Model):
    url = models.URLField()

class Room(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms')
    is_private = models.BooleanField(default=False)
    background = models.ForeignKey(Background, on_delete=models.SET_NULL, null=True, blank=True)
    enable_mic = models.BooleanField(default=True)

class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='participations')
    in_room = models.BooleanField(default=False)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    mic_allow = models.BooleanField(default=True)
    chat_allow = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)

class RoomSubject(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_subjects')
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name='room_subjects')

class Subject(models.Model):
    name = models.CharField(max_length=255)
