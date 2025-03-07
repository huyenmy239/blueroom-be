"""
ASGI config for blueroom project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from apps.chat.consumers import ChatConsumer
from apps.rooms.consumers import RoomConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blueroom.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": SessionMiddlewareStack(
        URLRouter([
            path('ws/room/<int:room_id>/', ChatConsumer.as_asgi()),
            path("ws/rooms/", RoomConsumer.as_asgi()),
        ])
    ),
})
