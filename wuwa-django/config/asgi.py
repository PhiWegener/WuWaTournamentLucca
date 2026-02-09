import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 1) Erst Django ASGI App initialisieren (lädt Apps/Registry)
django_asgi_app = get_asgi_application()

# 2) Danach erst routing importieren (dann dürfen consumers/models geladen werden)
import core.routing  # noqa: E402


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(core.routing.websocket_urlpatterns)
    ),
})
