from django.db import models
from apps.accounts.models import User


# Create your models here.

class Background(models.Model):
    id = models.BigAutoField(primary_key=True)
    bg = models.ImageField(upload_to='room-backgrounds/', null=True, blank=True)

    class Meta:
        db_table = 'backgrounds'
        # managed = False

    def __str__(self):
        return self.bg.url if self.bg else 'No background available'

class Room(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, db_column='created_by', related_name='rooms')
    is_private = models.BooleanField(default=False)
    background = models.ForeignKey(Background, on_delete=models.SET_NULL, db_column='background', null=True, blank=True)
    enable_mic = models.BooleanField(default=True)
    members = models.IntegerField(default=1)
    members_max = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    

    class Meta:
        db_table = 'rooms'
        # managed = False

    def __str__(self):
        return self.title

class Participation(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='participations')
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE, db_column='room_id', related_name='participants')
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    mic_allow = models.BooleanField(default=True)
    chat_allow = models.BooleanField(default=True)
    is_blocked = models.IntegerField(null=True)

    class Meta:
        db_table = 'participations'
        # managed = False

class Subject(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'subjects'
        # managed = False

    def __str__(self):
        return self.name

class RoomSubject(models.Model):
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE, db_column='room_id', related_name='subjects')
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column='subject_id', related_name='rooms')

    class Meta:
        db_table = 'room_subjects'
        # managed = False

        unique_together = ('room_id', 'subject_id')