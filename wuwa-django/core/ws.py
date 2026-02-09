from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from .models import Match
from .draft import buildDraftContext


def broadcastDraftUpdate(matchId: int):

    channelLayer = get_channel_layer()
    groupName = f"matchDraft_{matchId}"

    async_to_sync(channelLayer.group_send)(groupName, {"type": "draftUpdated", "payload": {"type": "refresh"}})
