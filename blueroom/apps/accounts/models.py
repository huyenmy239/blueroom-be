from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_user = models.BooleanField(default=True)
    is_busy = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'accounts'
        managed = False

    def __str__(self):
        return self.username