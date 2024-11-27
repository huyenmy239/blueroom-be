from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_busy = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    last_login = None
    is_superuser = None
    first_name = None
    last_name = None
    is_staff = None
    date_joined = None
    
    class Meta:
        db_table = 'accounts'
        # managed = False

    def __str__(self):
        return self.username


class Note(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, db_column='created_by', related_name="personal_notes")

    class Meta:
        db_table = 'notes'
        # managed = False

    def __str__(self):
        return self.title