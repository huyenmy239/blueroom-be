# apps/rooms/routing.py
from django.urls import re_path

from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/rooms/(?P<room_id>\d+)/$', ChatConsumer.as_asgi()),
]
