"""
ASGI config for blueroom project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# your_project_name/asgi.py

# your_project_name/asgi.py

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from apps.chat import consumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blueroom.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": SessionMiddlewareStack(
        URLRouter([
            path('ws/room/<int:room_id>/', consumers.ChatConsumer.as_asgi()),  # WebSocket URL
        ])
    ),
})
