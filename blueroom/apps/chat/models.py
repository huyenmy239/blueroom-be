from django.db import models
from rooms.models import Participation


# Create your models here.

class Message(models.Model):
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(
        max_length=10, 
        choices=[('text', 'Text'), ('file', 'File'), ('link', 'Link')]
    )