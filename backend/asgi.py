# import os
#
# from channels.auth import AuthMiddlewareStack
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from chat.routers import websocket_urlpatterns
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
# application = get_asgi_application()
#
# application = ProtocolTypeRouter({
#     "http": application,
#     "websocket": AuthMiddlewareStack(
#         URLRouter(websocket_urlpatterns)
#     )
# })

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from chat.routers import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
