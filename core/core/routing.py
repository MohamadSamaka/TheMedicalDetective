from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path, include, path
from django.core.asgi import get_asgi_application


from core.home.routing import websocket_urlspatterns
from core.home.consumers import Consumer


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlspatterns
            # [
            #     # websocket_urlspatterns
            #     # re_path(r'ws/socket-server/(?P<room_name>)/$', Consumer.as_asgi()),
            # ]
        )
    )
    
})
