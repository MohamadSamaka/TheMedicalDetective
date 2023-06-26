from django.urls import re_path
from core.home.consumers import Consumer


websocket_urlspatterns = [
    re_path(r'ws/socket-server/', Consumer.as_asgi()),
    # re_path(r'ws/socket-server/', Consumer.as_asgi()),
]