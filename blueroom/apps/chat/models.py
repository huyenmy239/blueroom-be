from django.db import models
from apps.rooms.models import Participation


# Create your models here.

class Message(models.Model):
    id = models.BigAutoField(primary_key=True)
    participation_id = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='messages', default=1)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(
        max_length=10, 
        choices=[('text', 'Text'), ('file', 'File'), ('link', 'Link')]
    )

    class Meta:
        db_table = 'messages'
        managed = False

    def __str__(self):
        return f'Message {self.message_id} in participation {self.participation_id}'