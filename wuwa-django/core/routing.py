from django.urls import re_path
from .consumers import MatchDraftConsumer

websocket_urlpatterns = [
    re_path(r"ws/match/(?P<matchId>\d+)/draft/$", MatchDraftConsumer.as_asgi()),
]
