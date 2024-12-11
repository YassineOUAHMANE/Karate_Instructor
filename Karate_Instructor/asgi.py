import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from user.consumers import RealTimeFeedbackConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Karate_Instructor.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter([
        path("ws/user/", RealTimeFeedbackConsumer.as_asgi()),
    ]),
})
